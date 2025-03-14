#  Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import unittest

import numpy as np
import paddle
import paddle.fluid as fluid
from tests.op_test import OpTest

paddle.enable_static()
SEED = 2021


def ref_leaky_relu(x, alpha=0.01):
    out = np.copy(x)
    out[out < 0] *= alpha
    return out


class TestLeadyRelu(OpTest):
    def setUp(self):
        self.set_npu()
        self.op_type = "leaky_relu"
        self.place = paddle.CustomPlace("npu", 0)

        self.init_dtype()
        np.random.seed(SEED)

        self.set_inputs()
        self.set_attrs()
        self.set_outputs()

    def set_inputs(self):
        x = np.random.uniform(-1, 1, [11, 17]).astype(self.dtype)
        self.inputs = {"X": OpTest.np_dtype_to_fluid_dtype(x)}

    def set_attrs(self):
        self.attrs = {}

    def set_outputs(self):
        alpha = 0.02 if "alpha" not in self.attrs else self.attrs["alpha"]
        out = ref_leaky_relu(self.inputs["X"], alpha)
        self.outputs = {"Out": out}

    def set_npu(self):
        self.__class__.use_custom_device = True

    def init_dtype(self):
        self.dtype = np.float32

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        if self.dtype == np.float16:
            self.check_grad_with_place(
                self.place, ["X"], "Out", max_relative_error=0.006
            )
        else:
            self.check_grad_with_place(self.place, ["X"], "Out")


class TestLeadyReluFP16(TestLeadyRelu):
    def init_dtype(self):
        self.dtype = np.float16


class TestLeadyRelu2(TestLeadyRelu):
    def set_attrs(self):
        self.attrs = {"alpha": 0.5}


class TestLeadyRelu3(TestLeadyRelu):
    def set_attrs(self):
        self.attrs = {"alpha": -0.5}


class TestLeakyReluNet(unittest.TestCase):
    def _test(self, run_npu=True):
        main_prog = paddle.static.Program()
        startup_prog = paddle.static.Program()
        main_prog.random_seed = SEED
        startup_prog.random_seed = SEED
        np.random.seed(SEED)

        x_np = np.random.random(size=(32, 32)).astype("float32")
        label_np = np.random.randint(2, size=(32, 1)).astype("int64")

        with paddle.static.program_guard(main_prog, startup_prog):
            x = paddle.static.data(name="x", shape=[32, 32], dtype="float32")
            label = paddle.static.data(name="label", shape=[32, 1], dtype="int64")

            y = paddle.nn.functional.leaky_relu(x)

            fc_1 = fluid.layers.fc(input=y, size=128)
            prediction = fluid.layers.fc(input=fc_1, size=2, act="softmax")

            cost = paddle.nn.functional.cross_entropy(input=prediction, label=label)
            loss = paddle.mean(cost)
            sgd = fluid.optimizer.SGD(learning_rate=0.01)
            sgd.minimize(loss)

        if run_npu:
            place = paddle.CustomPlace("npu", 0)
        else:
            place = paddle.CPUPlace()

        exe = paddle.static.Executor(place)
        exe.run(startup_prog)

        print("Start run on {}".format(place))
        for epoch in range(100):

            pred_res, loss_res = exe.run(
                main_prog,
                feed={"x": x_np, "label": label_np},
                fetch_list=[prediction, loss],
            )
            if epoch % 10 == 0:
                print(
                    "Epoch {} | Prediction[0]: {}, Loss: {}".format(
                        epoch, pred_res[0], loss_res
                    )
                )

        return pred_res, loss_res

    def test_npu(self):
        cpu_pred, cpu_loss = self._test(False)
        npu_pred, npu_loss = self._test(True)

        self.assertTrue(np.allclose(npu_pred, cpu_pred))
        self.assertTrue(np.allclose(npu_loss, cpu_loss))


if __name__ == "__main__":
    unittest.main()
