"""Prueba de humo acotada de H2O: arranca un clúster local, imprime versiones y lo apaga.

No ejecuta AutoML. Sirve para verificar qué versión de Java es suficiente para
``h2o==3.46.0.12`` en la máquina actual.

Uso (desde la raíz del repo, con el entorno virtual activo)::

    python h2o_demo/smoke_h2o.py
"""

from __future__ import annotations

import platform
import subprocess
import sys
import time


def java_version() -> str:
    """Devuelve la primera línea de ``java -version`` (o el error si Java no está instalado)."""
    try:
        proc = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"java no disponible: {exc}"
    lines = [ln for ln in proc.stderr.splitlines() if not ln.startswith("Picked up")]
    return lines[0] if lines else proc.stderr.strip()


def main() -> int:
    import h2o

    print(f"python: {platform.python_version()}")
    print(f"h2o (paquete Python): {h2o.__version__}")
    print(f"java: {java_version()}")
    start = time.perf_counter()
    h2o.init(nthreads=1, max_mem_size="1G")
    cluster = h2o.cluster()
    print(f"h2o.cluster().version: {cluster.version}")
    print(f"tiempo de arranque (s): {time.perf_counter() - start:.1f}")
    cluster.shutdown()
    print("clúster apagado correctamente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
