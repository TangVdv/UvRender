bl_info = {
    "name": "UV Animated Render",
    "description": "Render a scene with the UVs of selected meshes",
    "author": "TangVdv",
    "version": (1, 0),
    "blender": (3, 6, 5),
    "location": "VIEW_3D > N Panel > UV Render",
    "category": "Render",
    "github_url": "https://github.com/TangVdv/UvRender"
}

from .uv_render import *
