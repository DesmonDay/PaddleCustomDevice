# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import numpy as np
import paddle
import paddle.fluid as fluid
from tests.op_test import OpTest

paddle.enable_static()


def strided_slice_native_forward(input, axes, starts, ends, strides):
    dim = input.ndim
    start = []
    end = []
    stride = []
    for i in range(dim):
        start.append(0)
        end.append(input.shape[i])
        stride.append(1)

    for i in range(len(axes)):
        start[axes[i]] = starts[i]
        end[axes[i]] = ends[i]
        stride[axes[i]] = strides[i]

    result = {
        1: lambda input, start, end, stride: input[start[0] : end[0] : stride[0]],
        2: lambda input, start, end, stride: input[
            start[0] : end[0] : stride[0], start[1] : end[1] : stride[1]
        ],
        3: lambda input, start, end, stride: input[
            start[0] : end[0] : stride[0],
            start[1] : end[1] : stride[1],
            start[2] : end[2] : stride[2],
        ],
        4: lambda input, start, end, stride: input[
            start[0] : end[0] : stride[0],
            start[1] : end[1] : stride[1],
            start[2] : end[2] : stride[2],
            start[3] : end[3] : stride[3],
        ],
        5: lambda input, start, end, stride: input[
            start[0] : end[0] : stride[0],
            start[1] : end[1] : stride[1],
            start[2] : end[2] : stride[2],
            start[3] : end[3] : stride[3],
            start[4] : end[4] : stride[4],
        ],
        6: lambda input, start, end, stride: input[
            start[0] : end[0] : stride[0],
            start[1] : end[1] : stride[1],
            start[2] : end[2] : stride[2],
            start[3] : end[3] : stride[3],
            start[4] : end[4] : stride[4],
            start[5] : end[5] : stride[5],
        ],
    }[dim](input, start, end, stride)

    return result


class TestStridedSliceOp(OpTest):
    def setUp(self):
        self.initTestCase()
        self.set_npu()
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

        self.inputs = {"Input": self.input}
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts,
            "ends": self.ends,
            "strides": self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")

    def initTestCase(self):
        self.input = np.random.rand(100)
        self.axes = [0]
        self.starts = [2]
        self.ends = [7]
        self.strides = [1]
        self.infer_flags = [1]


class TestStridedSliceOp1(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(100)
        self.axes = [0]
        self.starts = [3]
        self.ends = [8]
        self.strides = [1]
        self.infer_flags = [1]


class TestStridedSliceOp2(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(100)
        self.axes = [0]
        self.starts = [5]
        self.ends = [0]
        self.strides = [-1]
        self.infer_flags = [1]


class TestStridedSliceOp3(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(100)
        self.axes = [0]
        self.starts = [-1]
        self.ends = [-3]
        self.strides = [-1]
        self.infer_flags = [1]


class TestStridedSliceOp4(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(3, 4, 10)
        self.axes = [0, 1, 2]
        self.starts = [0, -1, 0]
        self.ends = [2, -3, 5]
        self.strides = [1, -1, 1]
        self.infer_flags = [1, 1, 1]


class TestStridedSliceOp5(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(5, 5, 5)
        self.axes = [0, 1, 2]
        self.starts = [1, 0, 0]
        self.ends = [2, 1, 3]
        self.strides = [1, 1, 1]
        self.infer_flags = [1, 1, 1]


class TestStridedSliceOp6(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(5, 5, 5)
        self.axes = [0, 1, 2]
        self.starts = [1, -1, 0]
        self.ends = [2, -3, 3]
        self.strides = [1, -1, 1]
        self.infer_flags = [1, 1, 1]


class TestStridedSliceOp7(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(5, 5, 5)
        self.axes = [0, 1, 2]
        self.starts = [1, 0, 0]
        self.ends = [2, 2, 3]
        self.strides = [1, 1, 1]
        self.infer_flags = [1, 1, 1]


class TestStridedSliceOp8(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(1, 100, 1)
        self.axes = [1]
        self.starts = [1]
        self.ends = [2]
        self.strides = [1]
        self.infer_flags = [1]


class TestStridedSliceOp9(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(1, 100, 1)
        self.axes = [1]
        self.starts = [-1]
        self.ends = [-2]
        self.strides = [-1]
        self.infer_flags = [1]


class TestStridedSliceOp10(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(10, 10)
        self.axes = [0, 1]
        self.starts = [1, 0]
        self.ends = [2, 2]
        self.strides = [1, 1]
        self.infer_flags = [1, 1]


class TestStridedSliceOp11(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(3, 3, 3, 4)
        self.axes = [0, 1, 2, 3]
        self.starts = [1, 0, 0, 0]
        self.ends = [2, 2, 3, 4]
        self.strides = [1, 1, 1, 2]
        self.infer_flags = [1, 1, 1, 1]


class TestStridedSliceOp12(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(3, 3, 3, 4, 5)
        self.axes = [0, 1, 2, 3, 4]
        self.starts = [1, 0, 0, 0, 0]
        self.ends = [2, 2, 3, 4, 4]
        self.strides = [1, 1, 1, 1, 1]
        self.infer_flags = [1, 1, 1, 1]


class TestStridedSliceOp13(TestStridedSliceOp):
    def initTestCase(self):
        self.input = np.random.rand(3, 3, 3, 6, 7, 8)
        self.axes = [0, 1, 2, 3, 4, 5]
        self.starts = [1, 0, 0, 0, 1, 2]
        self.ends = [2, 2, 3, 1, 2, 8]
        self.strides = [1, 1, 1, 1, 1, 2]
        self.infer_flags = [1, 1, 1, 1, 1]


class TestStridedSliceOpBool(TestStridedSliceOp):
    def test_check_grad(self):
        pass


class TestStridedSliceOpBool1D(TestStridedSliceOpBool):
    def initTestCase(self):
        self.input = np.random.rand(100).astype("bool")
        self.axes = [0]
        self.starts = [3]
        self.ends = [8]
        self.strides = [1]
        self.infer_flags = [1]


class TestStridedSliceOpBool2D(TestStridedSliceOpBool):
    def initTestCase(self):
        self.input = np.random.rand(10, 10).astype("bool")
        self.axes = [0, 1]
        self.starts = [1, 0]
        self.ends = [2, 2]
        self.strides = [1, 1]
        self.infer_flags = [1, 1]


class TestStridedSliceOpBool3D(TestStridedSliceOpBool):
    def initTestCase(self):
        self.input = np.random.rand(3, 4, 10).astype("bool")
        self.axes = [0, 1, 2]
        self.starts = [0, -1, 0]
        self.ends = [2, -3, 5]
        self.strides = [1, -1, 1]
        self.infer_flags = [1, 1, 1]


class TestStridedSliceOpBool4D(TestStridedSliceOpBool):
    def initTestCase(self):
        self.input = np.random.rand(3, 3, 3, 4).astype("bool")
        self.axes = [0, 1, 2, 3]
        self.starts = [1, 0, 0, 0]
        self.ends = [2, 2, 3, 4]
        self.strides = [1, 1, 1, 2]
        self.infer_flags = [1, 1, 1, 1]


class TestStridedSliceOpBool5D(TestStridedSliceOpBool):
    def initTestCase(self):
        self.input = np.random.rand(3, 3, 3, 4, 5).astype("bool")
        self.axes = [0, 1, 2, 3, 4]
        self.starts = [1, 0, 0, 0, 0]
        self.ends = [2, 2, 3, 4, 4]
        self.strides = [1, 1, 1, 1, 1]
        self.infer_flags = [1, 1, 1, 1]


class TestStridedSliceOpBool6D(TestStridedSliceOpBool):
    def initTestCase(self):
        self.input = np.random.rand(3, 3, 3, 6, 7, 8).astype("bool")
        self.axes = [0, 1, 2, 3, 4, 5]
        self.starts = [1, 0, 0, 0, 1, 2]
        self.ends = [2, 2, 3, 1, 2, 8]
        self.strides = [1, 1, 1, 1, 1, 2]
        self.infer_flags = [1, 1, 1, 1, 1]


class TestStridedSliceOp_starts_ListTensor(OpTest):
    def setUp(self):
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.config()
        self.set_npu()

        starts_tensor = []
        for index, ele in enumerate(self.starts):
            starts_tensor.append(("x" + str(index), np.ones((1)).astype("int32") * ele))

        self.inputs = {"Input": self.input, "StartsTensorList": starts_tensor}
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts_infer,
            "ends": self.ends,
            "strides": self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [3, 3, 4]
        self.axes = [0, 1, 2]
        self.strides = [1, 1, 1]
        self.infer_flags = [1, -1, 1]
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

        self.starts_infer = [1, 10, 2]

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")


class TestStridedSliceOp_ends_ListTensor(OpTest):
    def setUp(self):
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.config()
        self.set_npu()

        ends_tensor = []
        for index, ele in enumerate(self.ends):
            ends_tensor.append(("x" + str(index), np.ones((1)).astype("int32") * ele))

        self.inputs = {"Input": self.input, "EndsTensorList": ends_tensor}
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts,
            "ends": self.ends_infer,
            "strides": self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 0]
        self.ends = [3, 3, 4]
        self.axes = [0, 1, 2]
        self.strides = [1, 1, 2]
        self.infer_flags = [1, -1, 1]
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

        self.ends_infer = [3, 1, 4]

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")


class TestStridedSliceOp_starts_Tensor(OpTest):
    def setUp(self):
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.config()
        self.set_npu()

        self.inputs = {
            "Input": self.input,
            "StartsTensor": np.array(self.starts, dtype="int32"),
        }
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            # 'starts': self.starts,
            "ends": self.ends,
            "strides": self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 3, 4]
        self.axes = [0, 1, 2]
        self.strides = [1, 1, 1]
        self.infer_flags = [-1, -1, -1]
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")


class TestStridedSliceOp_ends_Tensor(OpTest):
    def setUp(self):
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.config()
        self.set_npu()

        self.inputs = {
            "Input": self.input,
            "EndsTensor": np.array(self.ends, dtype="int32"),
        }
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts,
            # 'ends': self.ends,
            "strides": self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 3, 4]
        self.axes = [0, 1, 2]
        self.strides = [1, 1, 1]
        self.infer_flags = [-1, -1, -1]
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")


class TestStridedSliceOp_listTensor_Tensor(OpTest):
    def setUp(self):
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.set_npu()
        self.config()

        ends_tensor = []
        for index, ele in enumerate(self.ends):
            ends_tensor.append(("x" + str(index), np.ones((1)).astype("int32") * ele))

        self.inputs = {
            "Input": self.input,
            "StartsTensor": np.array(self.starts, dtype="int32"),
            "EndsTensorList": ends_tensor,
        }
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            # 'starts': self.starts,
            # 'ends': self.ends,
            "strides": self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, 0, 2]
        self.ends = [2, 3, 4]
        self.axes = [0, 1, 2]
        self.strides = [1, 1, 1]
        self.infer_flags = [-1, -1, -1]
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")


class TestStridedSliceOp_strides_Tensor(OpTest):
    def setUp(self):
        self.place = paddle.CustomPlace("npu", 0)
        self.op_type = "strided_slice"
        self.set_npu()
        self.config()

        self.inputs = {
            "Input": self.input,
            "StridesTensor": np.array(self.strides, dtype="int32"),
        }
        self.outputs = {"Out": self.output}
        self.attrs = {
            "axes": self.axes,
            "starts": self.starts,
            "ends": self.ends,
            # 'strides': self.strides,
            "infer_flags": self.infer_flags,
        }

    def set_npu(self):
        self.__class__.use_custom_device = True

    def config(self):
        self.input = np.random.random([3, 4, 5, 6]).astype("float64")
        self.starts = [1, -1, 2]
        self.ends = [2, 0, 4]
        self.axes = [0, 1, 2]
        self.strides = [1, -1, 1]
        self.infer_flags = [-1, -1, -1]
        self.output = strided_slice_native_forward(
            self.input, self.axes, self.starts, self.ends, self.strides
        )

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad_normal(self):
        self.check_grad_with_place(self.place, ["Input"], "Out")

    # Test python API


class TestStridedSliceAPI(unittest.TestCase):
    def test_1(self):
        input = np.random.random([3, 4, 5, 6]).astype("float64")
        minus_1 = fluid.layers.fill_constant([1], "int32", -1)
        minus_3 = fluid.layers.fill_constant([1], "int32", -3)
        starts = fluid.layers.data(
            name="starts", shape=[3], dtype="int32", append_batch_size=False
        )
        ends = fluid.layers.data(
            name="ends", shape=[3], dtype="int32", append_batch_size=False
        )
        strides = fluid.layers.data(
            name="strides", shape=[3], dtype="int32", append_batch_size=False
        )

        x = fluid.layers.data(
            name="x", shape=[3, 4, 5, 6], append_batch_size=False, dtype="float64"
        )
        out_1 = paddle.strided_slice(
            x, axes=[0, 1, 2], starts=[-3, 0, 2], ends=[3, 100, -1], strides=[1, 1, 1]
        )
        out_2 = paddle.strided_slice(
            x,
            axes=[0, 1, 3],
            starts=[minus_3, 0, 2],
            ends=[3, 100, -1],
            strides=[1, 1, 1],
        )
        out_3 = paddle.strided_slice(
            x,
            axes=[0, 1, 3],
            starts=[minus_3, 0, 2],
            ends=[3, 100, minus_1],
            strides=[1, 1, 1],
        )
        out_4 = paddle.strided_slice(
            x, axes=[0, 1, 2], starts=starts, ends=ends, strides=strides
        )

        out_5 = x[-3:3, 0:100:2, -1:2:-1]
        out_6 = x[minus_3:3:1, 0:100:2, :, minus_1:2:minus_1]
        out_7 = x[minus_1, 0:100:2, :, -1:2:-1]

        exe = fluid.Executor(place=paddle.CustomPlace("npu", 0))
        res_1, res_2, res_3, res_4, res_5, res_6, res_7 = exe.run(
            fluid.default_main_program(),
            feed={
                "x": input,
                "starts": np.array([-3, 0, 2]).astype("int32"),
                "ends": np.array([3, 2147483648, -1]).astype("int64"),
                "strides": np.array([1, 1, 1]).astype("int32"),
            },
            fetch_list=[out_1, out_2, out_3, out_4, out_5, out_6, out_7],
        )
        assert np.array_equal(res_1, input[-3:3, 0:100, 2:-1, :])
        assert np.array_equal(res_2, input[-3:3, 0:100, :, 2:-1])
        assert np.array_equal(res_3, input[-3:3, 0:100, :, 2:-1])
        assert np.array_equal(res_4, input[-3:3, 0:100, 2:-1, :])
        assert np.array_equal(res_5, input[-3:3, 0:100:2, -1:2:-1, :])
        assert np.array_equal(res_6, input[-3:3, 0:100:2, :, -1:2:-1])
        assert np.array_equal(res_7, input[-1, 0:100:2, :, -1:2:-1])

    def test_dygraph_op(self):
        x = paddle.zeros(shape=[3, 4, 5, 6], dtype="float32")
        axes = [1, 2, 3]
        starts = [-3, 0, 2]
        ends = [3, 2, 4]
        strides_1 = [1, 1, 1]
        sliced_1 = paddle.strided_slice(
            x, axes=axes, starts=starts, ends=ends, strides=strides_1
        )
        assert sliced_1.shape == (3, 2, 2, 2)


class TestStridedSliceTensorArray(unittest.TestCase):
    def setUp(self):
        self.shape = (3, 1)
        self.data = np.random.random(size=self.shape).astype("float32")
        self.axes = [0, 1]
        self.starts = [0, 0]
        self.ends = [0, 2]
        self.strides = [1]
        self.iter_num = 3
        self.place = paddle.CustomPlace("npu", 0)
        self.exe = fluid.Executor(self.place)

    def set_program_and_run(self, main_program, case_num):
        with fluid.program_guard(main_program):
            x = [
                fluid.data(name="x0", shape=self.shape, dtype="float32"),
                fluid.data(name="x1", shape=self.shape, dtype="float32"),
                fluid.data(name="x2", shape=self.shape, dtype="float32"),
                fluid.data(name="x3", shape=self.shape, dtype="float32"),
            ]

            for each_x in x:
                each_x.stop_gradient = False

            arr = paddle.tensor.create_array(dtype="float32")
            for i in range(4):
                idx = paddle.tensor.array_length(arr)
                arr = paddle.tensor.array_write(x=x[i], i=idx, array=arr)

            self.sliced_arr = output = arr[0:4:2]

            array = paddle.concat(output)
            loss = paddle.sum(array)
            fluid.backward.append_backward(loss)
            g_vars = list(
                map(
                    main_program.global_block().var,
                    [each_x.name + "@GRAD" for each_x in x],
                )
            )

            self.out, self.g_x0, self.g_x1, self.g_x2, self.g_x3 = self.exe.run(
                main_program,
                feed={
                    "x0": self.data,
                    "x1": self.data,
                    "x2": self.data,
                    "x3": self.data,
                },
                fetch_list=[output] + g_vars,
            )

    def test_case(self):
        main_program = fluid.Program()
        self.set_program_and_run(main_program, 1)

        numeric_output = [self.data, self.data]
        self.assertTrue(
            self.sliced_arr.type == fluid.core.VarDesc.VarType.LOD_TENSOR_ARRAY
        )
        np.testing.assert_array_equal(self.out, numeric_output)
        np.testing.assert_array_equal(self.g_x0, np.zeros_like(self.data))
        np.testing.assert_array_equal(self.g_x1, np.zeros_like(self.data))
        np.testing.assert_array_equal(self.g_x2, np.zeros_like(self.data))
        np.testing.assert_array_equal(self.g_x3, np.zeros_like(self.data))


if __name__ == "__main__":
    unittest.main()
