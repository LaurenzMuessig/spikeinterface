import os
import shutil

import pytest
from pathlib import Path

import spikeinterface.extractors as se
import spikeinterface.sorters as ss

if hasattr(pytest, "global_test_folder"):
    cache_folder = pytest.global_test_folder / "sorters"
else:
    cache_folder = Path("cache_folder") / "sorters"


os.environ["SINGULARITY_DISABLE_CACHE"] = "true"

# This can be used locally to test singularity or docker
CONTAINER_MODE = "singularity"  # "singularity" | "docker"

ON_GITHUB = os.getenv("CI")
if ON_GITHUB:
    CONTAINER_MODE = "singularity"


def check_gh_settings():
    if ON_GITHUB:
        si_dev_path = os.getenv("SPIKEINTERFACE_DEV_PATH")
        assert si_dev_path is not None, "Tests on GITHUB CI must run with the SPIKEINTERFACE_DEV_PATH"


def generate_run_kwargs():
    test_recording, _ = se.toy_example(duration=30, seed=0, num_channels=64, num_segments=1)
    test_recording = test_recording.save(name="toy")
    test_recording.set_channel_gains(1)
    test_recording.set_channel_offsets(1)
    run_kwargs = dict(recording=test_recording, verbose=True)
    if CONTAINER_MODE == "singularity":
        run_kwargs["singularity_image"] = True
    elif CONTAINER_MODE == "docker":
        run_kwargs["docker_image"] = True
    else:
        raise Exception("CONTAINER_MODE can be 'docker' or 'singularity'")
    return run_kwargs


@pytest.fixture(scope="module")
def run_kwargs():
    check_gh_settings()
    return generate_run_kwargs()


def test_spykingcircus(run_kwargs):
    sorting = ss.run_sorter("spykingcircus", output_folder=cache_folder / "spykingcircus", **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_mountainsort4(run_kwargs):
    sorting = ss.run_sorter("mountainsort4", output_folder=cache_folder / "mountainsort4", **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_mountainsort5(run_kwargs):
    sorting = ss.run_sorter("mountainsort5", output_folder=cache_folder / "mountainsort5", **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_tridesclous(run_kwargs):
    sorting = ss.run_sorter("tridesclous", output_folder=cache_folder / "tridesclous", **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_ironclust(run_kwargs):
    sorting = ss.run_sorter("ironclust", output_folder=cache_folder / "ironclust", fGpu=False, **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_waveclus(run_kwargs):
    sorting = ss.run_sorter(sorter_name="waveclus", output_folder=cache_folder / "waveclus", **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_hdsort(run_kwargs):
    sorting = ss.run_sorter(sorter_name="hdsort", output_folder=cache_folder / "hdsort", **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_kilosort1(run_kwargs):
    sorting = ss.run_sorter(sorter_name="kilosort", output_folder=cache_folder / "kilosort", useGPU=False, **run_kwargs)
    print("resulting sorting")
    print(sorting)


def test_combinato(run_kwargs):
    rec = run_kwargs["recording"]
    channels = rec.get_channel_ids()[0:1]
    rec_one_channel = rec.channel_slice(channels)
    run_kwargs["recording"] = rec_one_channel
    sorting = ss.run_sorter(sorter_name="combinato", output_folder=cache_folder / "combinato", **run_kwargs)
    print(sorting)


@pytest.mark.skip("Klusta is not supported anymore for Python>=3.8")
def test_klusta(run_kwargs):
    sorting = ss.run_sorter("klusta", output_folder=cache_folder / "klusta", **run_kwargs)
    print(sorting)


if __name__ == "__main__":
    kwargs = generate_run_kwargs()
    test_combinato(kwargs)
