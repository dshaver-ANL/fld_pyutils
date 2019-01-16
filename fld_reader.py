import numpy as np


class FldData:
    def __init__(self, filename, ndim=3):

        self.filename = filename

        # TODO: Check if this is consistent with nz ?
        self.ndim = ndim

        with open(self.filename, 'rb') as f:
            header_str = f.read(132).decode(encoding='ascii')
            header_list = header_str.split()

            self.float_size = int(header_list[1])
            self.nx = int(header_list[2])
            self.ny = int(header_list[3])
            self.nz = int(header_list[4])
            self.nelt = int(header_list[5])
            self.nelgt = int(header_list[6])
            self.time = float(header_list[7])
            self.iostep = int(header_list[8])
            self.fid0 = int(header_list[9])
            self.nfileoo = int(header_list[10])
            self.rdcode = header_list[11]
            self.p0th = float(header_list[12]),
            self.if_press_mesh = False if 'F' in header_list[13] else True

            endian_test_val = np.fromfile(f, dtype=np.float32, count=1)

            if self.float_size == 4:
                self.float_type = np.dtype(np.float32)
            elif self.float_size == 8:
                self.float_type = np.dtype(np.float64)
            else:
                raise ValueError('{} specified invalid float size {}'.format(self.filename, self.float_size))

            self.int_type = np.dtype(np.int32)

            if not np.all(np.isclose(endian_test_val, [6.54321], atol=1e-6, rtol=0.0)):
                self.float_type = self.float_type.newbyteorder('S')
                self.int_type = self.int_type.newbyteorder('S')

        self.glob_el_nums_offset = 136
        self.field_offset = 136 + self.nelt

    def get_glob_el_nums(self):
        with open(self.filename, 'rb') as f:
            f.seek(self.glob_el_nums_offset)
            return np.fromfile(f, dtype=self.int_type, count=self.nelt)

    def get_field(self):
        with open(self.filename, 'rb') as f:
            f.seek(self.field_offset)
            count = self.ndim * self.nx * self.ny * self.nz * self.nelt
            return np.fromfile(f, dtype=self.float_type, count=count).reshape([self.ndim, -1])

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        width = max(len(key) for key in self.__dict__)
        result = ''
        for k, v in self.__dict__.items():
            result += '{key:{width}} = {value}\n'.format(key=k, value=v, width=width)
        return result


if __name__ == '__main__':
    fld = FldData('data/test0.f00001')

    with open('header.txt', 'w') as f:
        print(fld, file=f)

    with open('glob_el_nums.txt', 'w') as f:
        glob_el_array = fld.get_glob_el_nums()
        glob_el_array.tofile(f, sep=' ', format='%3d')

    with open('field.txt', 'w') as f:
        fmt = '%.3e'
        fld_array = fld.get_field()
        for i in range(fld.ndim):
            fld_array[i:].tofile(f, sep=' ', format=fmt)
            f.write('\n')
