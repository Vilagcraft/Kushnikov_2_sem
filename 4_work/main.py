# =========================
# main.py
# =========================

import uvicorn
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from scipy.integrate import solve_ivp
import numpy as np
from pathlib import Path

app = FastAPI()

home = Path(__file__).parent

class Poly:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __call__(self, x):
        return (
            self.a * (x ** 3)
            + self.b * (x ** 2)
            + self.c * x
            + self.d
        )


def fit_cubic_solution(sol, var_index=0):

    t = sol.t
    x = sol.y[var_index]

    a, b, c, d = np.polyfit(t, x, 3)

    return (
        float(a),
        float(b),
        float(c),
        float(d)
    )


@app.get("/")
async def main():
    return FileResponse(home / "web" / "index.html")


# =========================================================
# ИСПРАВЛЕНО:
# endpoint без завершающего /
# =========================================================

@app.post("/api/glass")
async def glass_count(data=Body()):

    try:

        y0 = [
            value['y0']
            for _, value in data['params'].items()
        ]

        limits = [
            value['limit']
            for _, value in data['params'].items()
        ]

        norms = [
            value['norm']
            for _, value in data['params'].items()
        ]

        raw_poly = data['poly']
        raw_dist = data['dists']

        poly = {}

        for key, value in raw_poly.items():

            poly[int(key)] = Poly(
                value['a'],
                value['b'],
                value['c'],
                value['d']
            )

        dist = {}

        for key, value in raw_dist.items():

            dist[int(key)] = Poly(
                value['a'],
                value['b'],
                value['c'],
                value['d']
            )

        norm_dict = {
            i + 1: val
            for i, val in enumerate(norms)
        }

        t = np.linspace(0, 1, 50)

        solution = solve_ivp(
            dglass_dt,
            (0, 1),
            y0,
            t_eval=t,
            method='RK45',
            args=(poly, dist, norm_dict),
            dense_output=True
        )

        y = solution.sol(t)

        tf = [float(value) for value in t]

        yf = [
            [float(x) for x in row]
            for row in y
        ]

        approx = []

        for i in range(len(yf)):
            approx.append(
                fit_cubic_solution(solution, i)
            )

        return JSONResponse(content={
            "t": tf,
            "y": yf,
            "status": solution.status,
            "limits": limits,
            "approx": approx
        })

    except Exception as e:

        print(e)

        raise HTTPException(status_code=500)


# =========================================================
# ЭКОЛОГИЧЕСКАЯ МОДЕЛЬ СИСТЕМНОЙ ДИНАМИКИ
# =========================================================

def dglass_dt(t, u, f, z, norm):

    [
        x1_t,
        x2_t,
        x3_t,
        x4_t,
        x5_t,
        x6_t,
        x7_t,
        x8_t,
        x9_t,
        x10_t,
        x11_t,
        x12_t,
        x13_t,
        x14_t,
        x15_t,
        x16_t,
        x17_t,
        x18_t
    ] = u

    dx1_dt = (
        f[1](x3_t)
        + f[2](x4_t)
        + f[3](x12_t)
        - f[4](x18_t)
        - z[1](t)
    ) / norm[1]

    dx2_dt = (
        f[2](x17_t)
        - f[3](x3_t)
        - z[2](t)
    ) / norm[2]

    dx3_dt = (
        f[3](x10_t)
        + f[4](x15_t)
        + f[5](x16_t)
        - f[6](x2_t)
        - z[3](t)
    ) / norm[3]

    dx4_dt = (
        f[4](x11_t)
        + f[5](x13_t)
        - f[6](x5_t)
        - z[4](t)
    ) / norm[4]

    dx5_dt = (
        f[5](x17_t)
        - f[6](x3_t)
        - z[5](t)
    ) / norm[5]

    dx6_dt = (
        f[6](x17_t)
        - z[6](t)
    ) / norm[6]

    dx7_dt = (
        f[7](x17_t)
        - z[7](t)
    ) / norm[7]

    dx8_dt = (
        f[8](x17_t)
        - z[8](t)
    ) / norm[8]

    dx9_dt = (
        f[9](x17_t)
        - z[9](t)
    ) / norm[9]

    dx10_dt = (
        f[10](x17_t)
        - z[10](t)
    ) / norm[10]

    dx11_dt = (
        f[11](x5_t)
        - z[11](t)
    ) / norm[11]

    dx12_dt = (
        f[12](x5_t)
        - z[12](t)
    ) / norm[12]

    dx13_dt = (
        f[13](x5_t)
        - z[13](t)
    ) / norm[13]

    dx14_dt = (
        f[14](x9_t)
        - z[14](t)
    ) / norm[14]

    dx15_dt = (
        f[15](x17_t)
        - z[15](t)
    ) / norm[15]

    dx16_dt = (
        f[16](x17_t)
        - z[16](t)
    ) / norm[16]

    dx17_dt = (
        f[17](x9_t)
        - z[17](t)
    ) / norm[17]

    dx18_dt = (
        f[18](x5_t)
        - f[1](x1_t)
        - z[18](t)
    ) / norm[18]

    return [
        dx1_dt,
        dx2_dt,
        dx3_dt,
        dx4_dt,
        dx5_dt,
        dx6_dt,
        dx7_dt,
        dx8_dt,
        dx9_dt,
        dx10_dt,
        dx11_dt,
        dx12_dt,
        dx13_dt,
        dx14_dt,
        dx15_dt,
        dx16_dt,
        dx17_dt,
        dx18_dt
    ]


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )