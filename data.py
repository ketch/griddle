from clawpack import pyclaw
import os

class TimeSeries(dict):
    r"""A TimeSeries represents a time series of Solution objects.

        It is a dictionary whose keys are frame numbers and whose values
        are the corresponding frames (solutions).  The dictionary entries
        are populated only when actually requested.  The GDS knows how to
        load them either:

        1. from file, based on a path and extension; or
        2. from a controller or list of frames in memory.

        For now, it is assumed that frames are numbered from 0 to N and that
        all frames exist.  This could be made more general by modifying
        `list_frames` and `_get_num_data_files`.

        A TimeSeries can be initialized simply by providing a path
        to a set of output files:

            >>> import griddle
            >>> ts = griddle.data.TimeSeries('./test_data/_pyclaw_3d_shocktube/')

        The TimeSeries will automatically determine the data format
        and the number of frames in the series based on the files present:

            >>> ts.list_frames
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            >>> ts._data_format
            'hdf5'
    """
    @property
    def list_frames(self):
        if hasattr(self,'_frame_list'):
            return list(range(len(self._frame_list)))
        else:
            # Maybe we should get the actual file indices instead
            return list(range(_get_num_data_files(self._data_path,self._data_format)))

    def __getitem__(self, key):
        """Accept either integers or strings as keys.
           Load the requested frame if it is not cached already.
        """
        if type(key) is int:
            key = str(key)
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            try:
                self[key] = self._get_frame(int(key))
                return dict.__getitem__(self, key)
            except:
                print('Frame %s does not exist' % key)

    def __init__(self,path_or_list,file_format=None):
        """Set up the function _get_frame, which loads individual
           frames (either from memory or from file).
        """
        super(TimeSeries, self).__init__()

        if type(path_or_list) == str:
            # It's a path
            self._data_path = path_or_list
            if file_format is None:
                self._data_format = _get_data_format(self._data_path)
            else:
                self._data_format = file_format
            self._get_frame = lambda frame_num: \
                                      pyclaw.Solution(frame_num,
                                                      path=self._data_path,
                                                      file_format=self._data_format)
        elif hasattr(path_or_list, '__getitem__'):
            # It's a list of frames
            self._frame_list = path_or_list
            self._get_frame = lambda frame_num: self._frame_list[frame_num]
        else:
            raise Exception('TimeSeries must be initialized \
                    with a path or list of frames.')


def _get_num_data_files(path,file_format):
    r"""Count the number of output files of type file_format in directory
        specified by path.
    """
    files = os.listdir(path)
    file_string = file_substrings[file_format]
    data_files = [file_string in filename for filename in files]
    return data_files.count(True)


def _get_data_format(path):
    r"""Figure out which file format to read.

        Check which of the known file types are present in directory specified
        by `path`.  If multiple types are present, ask user which to use.
    """
    files = os.listdir(path)
    file_types_present = []
    for file_type, string in file_substrings.items():
        if any([string in filename for filename in files]):
            file_types_present.append(file_type)

    if len(file_types_present)==1:
        return file_types_present[0]
    else:
        return raw_input("""Multiple file types are present in the specified
                        data directory.  Which do you wish to use?
                        """+file_types_present)


file_substrings = {'ascii': 'fort.q',  # should be 'extensions'
                   'hdf5': 'hdf',
                   'petsc': 'ptc'}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
