# coding=utf-8
# Copyright 2025 The Google Research Authors.
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

# Copyright 2022 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Configures ScaNN to be built from source."""

import logging
import os

_BAZELRC = ".bazelrc"
_BAZEL_QUERY = ".bazel-query.sh"


# Writes variables to bazelrc file
def write_to_bazelrc(line):
  with open(_BAZELRC, "a") as f:
    f.write(line + "\n")


def write_action_env(var_name, var):
  write_to_bazelrc('build --action_env %s="%s"' % (var_name, str(var)))
  with open(_BAZEL_QUERY, "a") as f:
    f.write('{}="{}" '.format(var_name, var))


def generate_shared_lib_name(namespec):
  """Converts the linkflag namespec to the full shared library name."""
  # Assume Linux for now
  return namespec[1][3:]


def create_build_configuration():
  """Main function to create build configuration."""
  print()
  print("Configuring ScaNN to be built from source...")

  if os.path.isfile(_BAZELRC):
    os.remove(_BAZELRC)
  if os.path.isfile(_BAZEL_QUERY):
    os.remove(_BAZEL_QUERY)

  logging.disable(logging.WARNING)

  try:
    import tensorflow.compat.v2 as tf  # pylint: disable=g-import-not-at-top
  except ModuleNotFoundError:
    print(
        "Failed to import TensorFlow. Please install ScaNN dependencies before"
        " compiling ScaNN, for example with the command `pip-compile"
        " pyproject.toml --all-extras -o - | pip install -r /dev/stdin`.")
    return

  # pylint: disable=invalid-name
  _TF_CFLAGS = tf.sysconfig.get_compile_flags()
  _TF_LFLAGS = tf.sysconfig.get_link_flags()
  _TF_CXX11_ABI_FLAG = tf.sysconfig.CXX11_ABI_FLAG

  _TF_SHARED_LIBRARY_NAME = generate_shared_lib_name(_TF_LFLAGS)
  _TF_HEADER_DIR = _TF_CFLAGS[0][2:]
  _TF_SHARED_LIBRARY_DIR = _TF_LFLAGS[0][2:]
  # pylint: enable=invalid-name

  write_action_env("TF_HEADER_DIR", _TF_HEADER_DIR)
  write_action_env("TF_SHARED_LIBRARY_DIR", _TF_SHARED_LIBRARY_DIR)
  write_action_env("TF_SHARED_LIBRARY_NAME", _TF_SHARED_LIBRARY_NAME)
  write_action_env("TF_CXX11_ABI_FLAG", _TF_CXX11_ABI_FLAG)

  write_to_bazelrc("build --spawn_strategy=standalone")
  write_to_bazelrc("build --strategy=Genrule=standalone")
  write_to_bazelrc("build -c opt")

  print()
  print("Build configurations successfully written to", _BAZELRC)
  print()

  with open(_BAZEL_QUERY, "a") as f:
    f.write('bazel query "$@"')


if __name__ == "__main__":
  create_build_configuration()
