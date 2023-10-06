# pycollada

pycollada is a python module for creating, editing and loading
[COLLADA](https://www.khronos.org/collada/), which is a COLLAborative Design Activity
for establishing an interchange file format for interactive 3D applications.

The library allows you to load a COLLADA file and interact with it as a python
object. In addition, it supports creating a collada python object from scratch,
as well as in-place editing.

You can get help at the [pycollada mailing list](https://groups.google.com/d/forum/pycollada).

See the [pycollada Documentation](http://pycollada.readthedocs.org/) for more
information.

![Build Status](https://github.com/pycollada/pycollada/actions/workflows/python-package.yml/badge.svg)

## ogsadmin notes

This is a fork of [pycollada](https://github.com/pycollada) to allow custom node names. All changes 
are done in the [add-optional-node-name branch](https://github.com/ogsadmin/pycollada/tree/add-optional-node-name)
and integrated into the official build through the [pycollada pull request 131](https://github.com/pycollada/pycollada/pull/131).

The actual aim of this change is to make FreeCAD export the "correct" node names to the collada file, so a *.gltf file for web can be generated (and displayed/modified using [babylonjs](https://www.babylonjs.com/)). The main benefit is that this allows a workflow for converting step files to *.gltf files without loosing the structural (component names) information. 
This would work in combination with the updated FreeCAD Collada *.dae exporter (from the forum [A more user friendly Collada .dae exporter](https://forum.freecad.org/viewtopic.php?t=14613)).

The overall process is then as follows:
- import the *.stp file into FreeCAD
- select everything and export it as Collada (*.dae) file (using the updated collada exporter)
- use COLLADA2GLTF to convert the collada file to a gltf file

Here is a sample batch file:

    @echo off
    :: To use a STEP mode, open it in Freecad and export is as COLLADA (*.dae)
    set MODELPATH=..\models
    :: Use only filename without extension
    ::set FILENAME=MSTKN-H-S14-HM-WLAN-24V v5
    set FILENAME=Zellmodul
    ::.\collada2gltf\COLLADA2GLTF-bin "%MODELPATH%\%FILENAME%.dae" "%MODELPATH%\%FILENAME%.glTF"
    .\collada2gltf\COLLADA2GLTF-bin "%MODELPATH%\%FILENAME%.dae" "%MODELPATH%\%FILENAME%.glb" -b true




## Projects using pycollada

* [FreeCAD COLLADA Import/Export](https://www.freecadweb.org/)
* [Blender COLLADA Importer](https://github.com/skrat/bpycollada)
* [Meshtool](https://github.com/pycollada/meshtool)
* [SceneJS COLLADA Import](https://github.com/xeolabs/scenejs-pycollada)
* [Faces in Relief](https://itunes.apple.com/us/app/faces-in-relief/id571820477?ls=1&mt=8)
