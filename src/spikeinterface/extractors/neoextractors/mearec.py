from pathlib import Path
from typing import Union

import numpy as np

import probeinterface as pi

from .neobaseextractor import NeoBaseRecordingExtractor, NeoBaseSortingExtractor


class MEArecRecordingExtractor(NeoBaseRecordingExtractor):
    """
    Class for reading data from a MEArec simulated data.

    Based on :py:class:`neo.rawio.MEArecRawIO`

    Parameters
    ----------
    file_path: str
        The file path to load the recordings from.
    all_annotations: bool, default: False
        Load exhaustively all annotations from neo.
    """

    mode = "file"
    NeoRawIOClass = "MEArecRawIO"
    name = "mearec"

    def __init__(self, file_path: Union[str, Path], all_annotations: bool = False):
        neo_kwargs = self.map_to_neo_kwargs(file_path)
        NeoBaseRecordingExtractor.__init__(self, all_annotations=all_annotations, **neo_kwargs)

        self.extra_requirements.append("mearec")

        probe = pi.read_mearec(file_path)
        probe.annotations["mearec_name"] = str(probe.annotations["mearec_name"])
        self.set_probe(probe, in_place=True)
        self.annotate(is_filtered=True)

        if hasattr(self.neo_reader._recgen, "gain_to_uV"):
            self.set_channel_gains(self.neo_reader._recgen.gain_to_uV)

        self._kwargs.update({"file_path": str(file_path)})

    @classmethod
    def map_to_neo_kwargs(
        cls,
        file_path,
    ):
        neo_kwargs = {"filename": str(file_path), "load_spiketrains": False, "load_analogsignal": True}
        return neo_kwargs


class MEArecSortingExtractor(NeoBaseSortingExtractor):
    mode = "file"
    NeoRawIOClass = "MEArecRawIO"
    handle_spike_frame_directly = False
    name = "mearec"

    def __init__(self, file_path: Union[str, Path]):
        neo_kwargs = self.map_to_neo_kwargs(file_path)

        sampling_frequency = self.read_sampling_frequency(file_path=file_path)
        NeoBaseSortingExtractor.__init__(
            self, sampling_frequency=sampling_frequency, use_natural_unit_ids=True, **neo_kwargs
        )

        self._kwargs = {"file_path": str(file_path)}

    @classmethod
    def map_to_neo_kwargs(cls, file_path):
        neo_kwargs = {"filename": str(file_path), "load_spiketrains": True, "load_analogsignal": False}
        return neo_kwargs

    def read_sampling_frequency(self, file_path: Union[str, Path]) -> float:
        from h5py import File

        with File(file_path, "r") as f:
            info = f["info"]
            recordings = info["recordings"]
            sampling_frequency = recordings["fs"][()]

            if isinstance(sampling_frequency, bytes):
                sampling_frequency = sampling_frequency.decode("utf-8")
            elif isinstance(sampling_frequency, np.generic):
                sampling_frequency = sampling_frequency.item()

        return float(sampling_frequency)


def read_mearec(file_path):
    """Read a MEArec file.

    Parameters
    ----------
    file_path: str or Path
        Path to MEArec h5 file

    Returns
    -------
    recording: MEArecRecordingExtractor
        The recording extractor object
    sorting: MEArecSortingExtractor
        The sorting extractor object
    """
    recording = MEArecRecordingExtractor(file_path)
    sorting = MEArecSortingExtractor(file_path)
    return recording, sorting
