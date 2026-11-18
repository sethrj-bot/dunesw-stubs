# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack.package import *


class DunerecoStub(Package):
    """Dependency-free stub of dunereco: installs only the FHiCL (and any GDML)
    files that dunereco would install, with none of its reco/ML dependency chain.

    Files are installed flat into ``<prefix>/fcl`` (mirroring cetmodules'
    ``install_fhicl``, which squashes subdirectories) from every source
    directory that calls ``install_fhicl()``.
    """

    homepage = "https://github.com/DUNE/dunereco"
    git = "https://github.com/DUNE/dunereco"
    url = f"{git}/archive/v10_31_00d00.tar.gz"

    version(
        "10.31.00d00",
        sha256="869312046efac99f3e38f5e26280373a4dae444c7dbedf3a59210594cfc71b73",
    )

    def url_for_version(self, version):
        return f"{self.git}/archive/v{version.underscored}.tar.gz"

    def install(self, spec, prefix):
        mkdirp(prefix.fcl)
        installed = {}
        collisions = 0
        for root, dirs, files in os.walk("."):
            dirs.sort()
            if "CMakeLists.txt" not in files:
                continue
            with open(os.path.join(root, "CMakeLists.txt")) as f:
                if "install_fhicl(" not in f.read():
                    continue
            for name in sorted(files):
                if not name.endswith(".fcl"):
                    continue
                if name in installed:
                    collisions += 1
                installed[name] = os.path.join(root, name)
        for name, src in installed.items():
            install(src, join_path(prefix.fcl, name))
        tty.msg(f"Installed {len(installed)} fcl files ({collisions} name collisions overwritten)")
        if os.path.isdir("gdml"):
            install_tree("gdml", prefix.gdml)

    def setup_run_environment(self, env):
        env.append_path("FHICL_FILE_PATH", self.prefix.fcl)
        env.append_path("FW_SEARCH_PATH", self.prefix.gdml)

    def setup_dependent_run_environment(self, env, dependent_spec):
        self.setup_run_environment(env)
