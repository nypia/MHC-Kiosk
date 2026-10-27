"""Render the build animation and/or the hero stills.

With Blender (recommended on a GPU machine):
    blender -b kiosk.blend -P render.py -- --final            # 1920x1080 animation + MP4
    blender -b kiosk.blend -P render.py -- --stills           # 4K C01-C04 stills
    blender -b kiosk.blend -P render.py -- --preview --step 6 # quick low-res check
With the bpy pip module:
    python render.py --preview --frames 1,240,480

Frames are written one PNG per frame and existing ones are skipped, so an
interrupted render resumes where it stopped (delete out/<mode>/frames to redo).
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import bpy  # noqa: E402

from kiosk import config as C  # noqa: E402

MODES = {
    #            resolution     samples  stills res      still samples
    "preview": ((960, 540), 24, (1280, 720), 48),
    "final": ((1920, 1080), 160, (3840, 2160), 512),
}


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="low-res, few samples (default)")
    ap.add_argument("--final", action="store_true", help="full quality")
    ap.add_argument("--stills", action="store_true", help="render C01-C04 instead of the animation")
    ap.add_argument("--frames", help="e.g. 1,240,480 or 100-200 (default: whole animation)")
    ap.add_argument("--step", type=int, default=1, help="render every Nth frame")
    ap.add_argument("--samples", type=int, help="override sample count")
    ap.add_argument("--res", help="override resolution, e.g. 1280x720")
    ap.add_argument("--cams", help="comma-separated still names to render, e.g. C01,C04")
    ap.add_argument("--cpu", action="store_true", help="never use the GPU")
    ap.add_argument("--no-video", action="store_true", help="skip MP4 encoding")
    return ap.parse_args(argv)


def slug(name):
    s = unicodedata.normalize("NFKD", name.replace("ı", "i")).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def use_gpu(scene, cpu_only):
    scene.cycles.device = "CPU"
    if cpu_only:
        return "CPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
            prefs.refresh_devices()
        except TypeError:
            continue
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            scene.cycles.device = "GPU"
            return f"{kind}: " + ", ".join(d.name for d in gpus)
    return "CPU"


def frames_from(spec, step):
    if not spec:
        return list(range(1, C.FRAMES + 1, step))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = map(int, part.split("-"))
            out += list(range(a, b + 1, step))
        else:
            out.append(int(part))
    return out


def configure(scene, res, samples):
    r = scene.render
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_depth = "8"
    r.use_persistent_data = True
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.02 if samples < 100 else 0.01


def render_frames(scene, frames, folder):
    folder.mkdir(parents=True, exist_ok=True)
    done = []
    for i, fr in enumerate(frames):
        path = folder / f"{fr:04d}.png"
        done.append(path)
        if path.exists():
            continue
        scene.frame_set(fr)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        print(f"[{i + 1}/{len(frames)}] frame {fr} -> {path.name}", flush=True)
    return done


def encode(files, fps, mp4):
    files = [f for f in files if f.exists()]
    if len(files) < 2:
        return
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        lst = mp4.with_suffix(".txt")
        lst.write_text("".join(f"file '{f.resolve().as_posix()}'\nduration {1 / fps:.6f}\n" for f in files)
                       + f"file '{files[-1].resolve().as_posix()}'\n")
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-vf", f"fps={fps}", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                        "-pix_fmt", "yuv420p", str(mp4)], check=True)
        lst.unlink()
    else:  # no ffmpeg on PATH (typical on Windows): let Blender's sequencer encode
        enc = bpy.data.scenes.new("encode")
        ed = enc.sequence_editor_create()
        strips = getattr(ed, "strips", None) or ed.sequences
        strip = strips.new_image("frames", str(files[0]), 1, 1)
        for f in files[1:]:
            strip.elements.append(f.name)
        enc.frame_start, enc.frame_end = 1, len(files)
        enc.render.fps = round(fps)
        enc.render.resolution_x, enc.render.resolution_y = bpy.context.scene.render.resolution_x, \
            bpy.context.scene.render.resolution_y
        enc.render.image_settings.file_format = "FFMPEG"
        enc.render.ffmpeg.format = "MPEG4"
        enc.render.ffmpeg.codec = "H264"
        enc.render.ffmpeg.constant_rate_factor = "HIGH"
        enc.render.filepath = str(mp4)
        bpy.ops.render.render(animation=True, scene=enc.name)
    print("video ->", mp4)


def main():
    args = parse()
    mode = "final" if args.final else "preview"
    if not bpy.data.filepath:
        bpy.ops.wm.open_mainfile(filepath=str(C.ROOT / "kiosk.blend"))
    scene = bpy.context.scene
    print("device:", use_gpu(scene, args.cpu))
    anim_res, anim_spp, still_res, still_spp = MODES[mode]
    if args.res:
        anim_res = still_res = tuple(map(int, args.res.lower().split("x")))
    if mode == "preview":
        scene.render.use_motion_blur = False
    out = C.OUT / mode

    if args.stills:
        configure(scene, still_res, args.samples or still_spp)
        wanted = args.cams.split(",") if args.cams else None
        for cam in sorted((o for o in scene.objects if o.type == "CAMERA" and "still_frame" in o),
                          key=lambda o: o.name):
            if wanted and not any(cam.name.startswith(w) for w in wanted):
                continue
            scene.camera = cam
            scene.render.use_motion_blur = False
            render_frames(scene, [int(cam["still_frame"])], out / "stills" / slug(cam.name))
            src = out / "stills" / slug(cam.name) / f"{int(cam['still_frame']):04d}.png"
            shutil.copy(src, out / "stills" / f"{slug(cam.name)}.png")
            print("still ->", out / "stills" / f"{slug(cam.name)}.png")
        return

    configure(scene, anim_res, args.samples or anim_spp)
    files = render_frames(scene, frames_from(args.frames, args.step), out / "frames")
    if not args.no_video and not args.frames:
        encode(files, C.FPS / args.step, out / ("kiosk_build.mp4" if mode == "final" else "kiosk_preview.mp4"))


if __name__ == "__main__":
    main()
