# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack.package import *


class DunedataprepStub(Package):
    """Dependency-free stub of dunedataprep: installs only the FHiCL (and any GDML)
    files that dunedataprep would install, with none of its reco/ML dependency chain.

    Files are installed flat into ``<prefix>/fcl`` (mirroring cetmodules'
    ``install_fhicl``, which squashes subdirectories) from every source
    directory that calls ``install_fhicl()``.
    """

    homepage = "https://github.com/DUNE/dunedataprep"
    git = "https://github.com/DUNE/dunedataprep"
    url = f"{git}/archive/v10_31_00d00.tar.gz"

    version(
        "10.31.00d00",
        sha256="5e641b2e7353c469aec370900ee66a9f8b337dd6eadc2969b64caf6ce8626091",
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
