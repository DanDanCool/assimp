import jmake
import shutil
from pathlib import Path

jmake.setupenv()

host = jmake.Host()
if host.mode == 'generate':
    jmake.configure_file(jmake.fullpath('revision.h.in')[0], jmake.fullpath('code/Common/revision.h')[0], {
        'GIT_COMMIT_HASH': '28ab0a09',
        'GIT_BRANCH': 'master',
        'ASSIMP_VERSION_MAJOR': 5,
        'ASSIMP_VERSION_MINOR': 3,
        'ASSIMP_VERSION_PATCH': 0,
        'ASSIMP_PACKAGE_VERSION': 0,
        'CMAKE_SHARED_LIBRARY_PREFIX': 'lib',
        'LIBRARY_SUFFIX': '',
        'CMAKE_DEBUG_POSTFIX': '',
        })
    jmake.configure_file(jmake.fullpath('contrib/zlib/zconf.h.in')[0], jmake.fullpath('contrib/zlib/zconf.h')[0])
    jmake.configure_file(jmake.fullpath('include/assimp/config.h.in')[0], jmake.fullpath('include/assimp/config.h')[0])

workspace = jmake.Workspace('assimp')

assimp_contrib = jmake.Project('assimp_contrib', jmake.Target.STATIC_LIBRARY)
debug = assimp_contrib.filter('debug')
debug['debug'] = True

unzip_files = jmake.glob('contrib/unzip', ['*.h', '*.c'])
poly2tri_files = jmake.glob('contrib/poly2tri/poly2tri', ['*.h', '*.cc'])
clipper_files = jmake.glob('contrib/clipper', ['*.hpp', '*.cpp'])
openddl_files = jmake.glob('contrib/openddlparser/code', '*.cpp') + jmake.glob('contrib/openddlparser/include', '*.h')
open3dgc_files = jmake.glob('contrib/Open3DGC', ['*.h', '*.cpp', '*.inl'])
zip_files = jmake.glob('contrib/zip/src', ['*.h', '*.c'])
pugixml_files = jmake.glob('contrib/pugixml/src', ['*.hpp', '*.cpp'])
stb_files = jmake.glob('contrib/stb', '*.h')
zlib_files = jmake.glob('contrib/zlib', ['*.h', '*.c'])

assimp_contrib.add(unzip_files + poly2tri_files + clipper_files + openddl_files + open3dgc_files +
                      zip_files + pugixml_files + stb_files + zlib_files)
assimp_contrib.include(jmake.fullpath('contrib/zlib'))
assimp_contrib.include(jmake.fullpath('contrib/openddlparser/include'))
assimp_contrib.include(jmake.fullpath('include'))

assimp_contrib.define('MINIZ_USE_UNALIGNED_LOADS_AND_STORES', 0)

assimp = jmake.Project('assimp', jmake.Target.STATIC_LIBRARY)
debug = assimp.filter('debug')
debug['debug'] = True

assimp_files = []
for dir in ['CApi', 'Common', 'Geometry', 'Material', 'Pbrt', 'PostProcessing']:
    assimp_files.extend(jmake.glob(f'code/{dir}', ['**/*.h', '**/*.cpp', '**/*.inl']))

filter = { 'C4D', 'IFC' }
for asset in Path(jmake.fullpath('code/AssetLib')[0]).glob('*'):
    if asset.stem in filter: continue
    assimp_files.extend(jmake.glob(str(asset), ['**/*.h', '**/*.cpp', '**/*.inl']))

rapidjson_files = jmake.glob('contrib/rapidjson/include', '**/*.h')
utf8cpp_files = jmake.glob('contrib/utf8cpp/source', '**/*.h')

assimp.add(assimp_files + rapidjson_files + utf8cpp_files)

assimp.include(jmake.fullpath(['include', 'code', '.']))
assimp.include(jmake.fullpath(['contrib', 'contrib/pugixml/src', 'contrib/unzip', 'contrib/rapidjson/include',
                               'contrib/zlib', 'contrib/openddlparser/include']))

if host.os == jmake.Platform.WIN32:
    assimp_contrib.define('_CRT_SECURE_NO_DEPRECATE', 1)
    assimp_contrib.define('_CRT_NONSTDC_NO_DEPRECATE', 1)
    assimp_contrib.define('_SILENCE_TR1_NAMESPACE_DEPRECATION_WARNING', 1)
    assimp_contrib.define('OPENDDLPARSER_BUILD', 1)

    assimp.define('_CRT_SECURE_NO_DEPRECATE', 1)
    assimp.define('RAPIDJSON_NOMEMBERITERATORCLASS', 1)
    assimp.define('RAPIDJSON_HAS_STDSTRING', 1)

assimp.depend(assimp_contrib)

assimp.export(includes=jmake.fullpath('include'))

workspace.add(assimp_contrib)
workspace.add(assimp)

jmake.generate(workspace)
