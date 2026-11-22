{
  description = "python-sonicare: talk to a Philips Sonicare toothbrush via Bluetooth LE";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});

      pythonFor = pkgs: pkgs.python3.withPackages (ps: [
        ps.gatt
        ps.dbus-python
        ps.pygobject3
        ps.pyqt5
        ps.matplotlib
        ps.numpy
      ]);

      # Qt needs to find its platform plugins (xcb, wayland)
      qtEnv = pkgs: ''
        export QT_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}:${pkgs.qt5.qtwayland.bin}/${pkgs.qt5.qtbase.qtPluginPrefix}"
      '';
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [ (pythonFor pkgs) ];
          shellHook = qtEnv pkgs + ''
            export PYTHONPATH="$PWD''${PYTHONPATH:+:$PYTHONPATH}"
            echo "python-sonicare: 'python examples/gui/run.py' (set SONICARE_MAC), 'python -m unittest discover -s tests'"
          '';
        };
      });

      apps = forAllSystems (pkgs: {
        # SONICARE_MAC=24:E5:AA:.. nix run
        default = self.apps.${pkgs.system}.gui;

        gui = {
          type = "app";
          program = toString (pkgs.writeShellScript "sonicare-gui" ''
            ${qtEnv pkgs}
            cd ${self}
            exec ${pythonFor pkgs}/bin/python examples/gui/run.py "$@"
          '');
        };

        test = {
          type = "app";
          program = toString (pkgs.writeShellScript "sonicare-test" ''
            cd ${self}
            exec ${pythonFor pkgs}/bin/python -m unittest discover -s tests "$@"
          '');
        };
      });

      checks = forAllSystems (pkgs: {
        tests = pkgs.runCommand "sonicare-tests" { } ''
          cd ${self}
          ${pythonFor pkgs}/bin/python -B -m unittest discover -s tests
          touch $out
        '';
      });
    };
}
