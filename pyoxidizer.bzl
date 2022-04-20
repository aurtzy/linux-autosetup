def make_exe():
    dist = default_python_distribution()

    policy = dist.make_python_packaging_policy()
    policy.resources_location_fallback = "filesystem-relative:lib"

    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "propellant.__main__"

    # Set initial value for `sys.path`. If the string `$ORIGIN` exists in
    # a value, it will be expanded to the directory of the built executable.
    # python_config.module_search_paths = ["$ORIGIN/lib"]

    exe = dist.to_python_executable(
        name="propellant",

        # If no argument passed, the default `PythonPackagingPolicy` for the
        # distribution is used.
        packaging_policy=policy,

        # If no argument passed, the default `PythonInterpreterConfig` is used.
        config=python_config,
    )
    exe.add_python_resources(exe.pip_download(["ruamel.yaml>=0.17, <0.18"]))

    exe.add_python_resources(exe.read_package_root(
        path=".",
        packages=["propellant"],
    ))
    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()


register_target("exe", make_exe)
register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)

resolve_targets()
