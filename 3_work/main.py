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
        x5_t
    ] = u

    # X1 — потери от заболеваемости населения
    dx1_dt = (
        f[1](x1_t)
        - z[1](t)
    ) / norm[1]

    # X2 — потери сельского хозяйства
    dx2_dt = (
        f[2](x2_t)
        - z[2](t)
    ) / norm[2]

    # X3 — потери природной среды
    dx3_dt = (
        f[3](x3_t)
        - z[3](t)
    ) / norm[3]

    # X4 — потери качества жизни
    dx4_dt = (
        f[4](x4_t)
        - z[4](t)
    ) / norm[4]

    # X5 — потери предприятия
    dx5_dt = (
        f[5](x5_t)
        - z[5](t)
    ) / norm[5]

    return [
        dx1_dt,
        dx2_dt,
        dx3_dt,
        dx4_dt,
        dx5_dt
    ]


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )