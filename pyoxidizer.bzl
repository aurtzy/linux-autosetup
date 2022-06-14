def make_exe():
    dist = default_python_distribution()

    policy = dist.make_python_packaging_policy()
    policy.resources_location_fallback = "filesystem-relative:lib"

    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "scriptman.__main__"

    exe = dist.to_python_executable(
        name="scriptman",
        packaging_policy=policy,
        config=python_config,
    )
    exe.add_python_resources(exe.pip_download(["ruamel.yaml~=0.17"]))
    exe.add_python_resources(exe.read_package_root(
        path=".",
        packages=["scriptman"],
    ))
    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()


register_target("exe", make_exe)
register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)

resolve_targets()
