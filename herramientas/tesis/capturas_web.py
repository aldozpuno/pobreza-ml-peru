"""Capturas de la web de resultados para la tesis (Figura 14 y Anexo 7).

Abre la web en Edge o Chrome sin ventana y fotografía cada gráfico completo, recortando por
los bordes del elemento y no por la ventana, de modo que ninguno queda cortado.

Requisitos: la web sirviéndose (`cd web && npm start`, o `npm run preview`) y Edge o Chrome.
Uso: python capturas_web.py [http://localhost:4500]
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket  # paquete websocket-client

SALIDA = Path(__file__).parent / "figuras"
ANCHO, ALTO, ESCALA = 1200, 900, 1.6  # ventana en px CSS y densidad de la captura
NAVEGADORES = ["msedge", "chrome", "chromium",
               r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Google\Chrome\Application\chrome.exe"]

# archivo → (ruta de la web, expresión JS con los elementos que deben entrar completos, margen en px).
# Las tarjetas de figura llevan margen para que se vea su borde; los bloques de página no, para
# que no asome la cabecera ni la tarjeta vecina.
CAPTURAS = {
    "fig_web": ("/territorio", "[fig(0)]", 14),
    "web_panorama": ("/", "[q('.portada'), bloque(0)]", 0),
    "web_lecturas": ("/", "[bloque(1)]", 0),
    "web_area": ("/", "[fig(1)]", 14),
    "web_sesgo": ("/territorio", "[fig(1)]", 14),
    "web_por_anio": ("/modelo", "[fig(1)]", 14),
    "web_matriz": ("/modelo", "[fig(3)]", 14),
    "web_curvas": ("/modelo", "[q('.dos-columnas')]", 14),
    "web_calibracion": ("/modelo", "[fig(6)]", 14),
    "web_variables": ("/variables", "[fig(0)]", 14),
    "web_periodos": ("/variables", "[fig(2)]", 14),
}
AYUDAS = ("const q = s => document.querySelector(s);"
          "const fig = i => document.querySelectorAll('app-figura')[i];"
          "const bloque = i => document.querySelectorAll('section.bloque')[i];")


def _navegador() -> str:
    for nombre in NAVEGADORES:
        ruta = shutil.which(nombre) or (nombre if Path(nombre).exists() else None)
        if ruta:
            return ruta
    raise RuntimeError("No se encontró Edge ni Chrome")


class Pestana:
    """Cliente mínimo del protocolo de depuración del navegador (CDP)."""

    def __init__(self, puerto: int):
        pedido = urllib.request.Request(f"http://127.0.0.1:{puerto}/json/new?about:blank", method="PUT")
        destino = json.load(urllib.request.urlopen(pedido, timeout=10))
        self.ws = websocket.create_connection(destino["webSocketDebuggerUrl"], timeout=60,
                                              suppress_origin=True)
        self.n = 0

    def orden(self, metodo: str, **parametros):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": metodo, "params": parametros}))
        while True:
            respuesta = json.loads(self.ws.recv())
            if respuesta.get("id") == self.n:
                if "error" in respuesta:
                    raise RuntimeError(f"{metodo}: {respuesta['error']}")
                return respuesta["result"]

    def js(self, expresion: str):
        r = self.orden("Runtime.evaluate", expression=expresion, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise RuntimeError(f"JS: {r['exceptionDetails'].get('text')} en {expresion[:80]}")
        return r["result"].get("value")


def capturar(base: str = "http://localhost:4500") -> list[Path]:
    SALIDA.mkdir(exist_ok=True)
    perfil = tempfile.mkdtemp(prefix="capturas_web_")
    puerto = 9377
    proceso = subprocess.Popen([_navegador(), "--headless=new", f"--remote-debugging-port={puerto}",
                                f"--user-data-dir={perfil}", "--hide-scrollbars", "--no-first-run",
                                "--disable-gpu", f"--window-size={ANCHO},{ALTO}", "about:blank"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    hechas = []
    try:
        for _ in range(60):  # espera a que el navegador abra el puerto
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{puerto}/json/version", timeout=1)
                break
            except OSError:
                time.sleep(0.25)
        p = Pestana(puerto)
        p.orden("Page.enable")
        p.orden("Emulation.setDeviceMetricsOverride", width=ANCHO, height=ALTO,
                deviceScaleFactor=ESCALA, mobile=False)
        p.orden("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
        ruta_actual = None
        for archivo, (ruta, elementos, margen) in CAPTURAS.items():
            if ruta != ruta_actual:
                p.orden("Page.navigate", url=f"{base}/#{ruta}")
                ruta_actual = ruta
                for _ in range(80):  # espera a que la página dibuje sus gráficos
                    lista = p.js("document.querySelectorAll('app-figura svg, app-figura table').length > 0"
                                 " && document.fonts.status === 'loaded'")
                    if lista:
                        break
                    time.sleep(0.25)
                else:
                    raise RuntimeError(f"La página {ruta} no terminó de cargar en {base}")
                time.sleep(1.5)  # transiciones y medición del ancho de los gráficos
            caja = p.js(f"(() => {{ {AYUDAS} const es = {elementos}.filter(Boolean);"
                        "if (!es.length) return null;"
                        "const r = es.map(e => e.getBoundingClientRect());"
                        "const x0 = Math.min(...r.map(c => c.left)), y0 = Math.min(...r.map(c => c.top));"
                        "const x1 = Math.max(...r.map(c => c.right)), y1 = Math.max(...r.map(c => c.bottom));"
                        "return {x: x0 + scrollX, y: y0 + scrollY, w: x1 - x0, h: y1 - y0}; })()")
            if not caja or caja["w"] < 50 or caja["h"] < 50:
                raise RuntimeError(f"{archivo}: no se encontró el elemento en {ruta}")
            imagen = p.orden("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                             clip={"x": max(0, caja["x"] - margen), "y": max(0, caja["y"] - margen),
                                   "width": caja["w"] + 2 * margen, "height": caja["h"] + 2 * margen, "scale": 1})
            destino = SALIDA / f"{archivo}.png"
            destino.write_bytes(base64.b64decode(imagen["data"]))
            hechas.append(destino)
            print(f"{destino.name}: {round(caja['w'])} × {round(caja['h'])} px")
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()
        shutil.rmtree(perfil, ignore_errors=True)
    return hechas


if __name__ == "__main__":
    capturar(*sys.argv[1:2])
