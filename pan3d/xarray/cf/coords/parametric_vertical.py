"""
Based on Parametric Vertical Coordinates appendix from CF-1.12 spec

https://cfconventions.org/Data/cf-conventions/cf-conventions-1.12/cf-conventions.html#parametric-v-coord
"""

import math
import sys
import inspect

CONVENTION_BASE_URL = "https://cfconventions.org/Data/cf-conventions/cf-conventions-1.12/cf-conventions.html"


# -----------------------------------------------------------------------------
# Factory method
# -----------------------------------------------------------------------------
def get_formula(xr_dataset, name, bias=0, scale=1):
    array_attributes = xr_dataset[name].attrs
    std_name = array_attributes.get("standard_name")
    formula_terms = array_attributes.get("formula_terms")

    formula_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for klass_name, klass in formula_classes:
        if std_name == klass.name:
            return FormulaAdapter(
                klass(xr_dataset, **extract_formula_terms(formula_terms)),
                bias=bias,
                scale=scale,
            )

    return None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def extract_formula_terms(formula_terms: str):
    tokens = formula_terms.split(" ")
    if len(tokens) % 2 != 0:
        msg = f"Invalid key/value pairing: {tokens}"
        raise ValueError(msg)

    key_mapping = {}
    nb_keys = int(len(tokens) / 2)
    for i in range(nb_keys):
        k = tokens[i * 2][:-1]
        v = tokens[i * 2 + 1]
        key_mapping[k] = v

    return key_mapping


# -----------------------------------------------------------------------------
class AbstractFormula:
    name = "__abstract__"

    def __init__(self, xr_dataset, **name_mapping):
        for k, v in name_mapping.items():
            setattr(self, k, xr_dataset[v].values)

        self.select_formula(name_mapping)

    def select_formula(self, name_mapping):
        pass


class FormulaAdapter:
    name = "__internal__"

    def __init__(self, formula, bias=0, scale=1):
        self._fn = formula
        self._bias = bias
        self._scale = scale
        print(f"{bias=} {scale=}")

    def __call__(self, n=0, k=0, j=0, i=0):
        return self._bias + self._scale * self._fn(n=n, k=k, j=j, i=i)


# -----------------------------------------------------------------------------
# Atmosphere natural log pressure coordinate
# -----------------------------------------------------------------------------
class AtmosphereNaturalLogPressureCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#atmosphere-natural-log-pressure-coordinate"
    name = "atmosphere_ln_pressure_coordinate"
    name_computed = "air_pressure"
    std_p0 = "reference_air_pressure_for_atmosphere_vertical_coordinate"

    def __len__(self):
        return 1

    def __call__(self, k, **_):
        return self.p0 * math.exp(-self.lev[k])


# -----------------------------------------------------------------------------
# Atmosphere sigma coordinate
# -----------------------------------------------------------------------------
class AtmosphereSigmaCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_atmosphere_sigma_coordinate"
    name = "atmosphere_sigma_coordinate"
    name_computed = "air_pressure"
    std_ptop = "air_pressure_at_top_of_atmosphere_model"
    std_ps = "surface_air_pressure"

    def __len__(self):
        return 4

    def __call__(self, n, k, j, i):
        return self.ptop + self.sigma[k] * (self.ps[n, j, i] - self.ptop)


# -----------------------------------------------------------------------------
# Atmosphere hybrid sigma pressure coordinate
# -----------------------------------------------------------------------------
class AtmosphereHybridSigmaPressureCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_atmosphere_hybrid_sigma_pressure_coordinate"
    name = "atmosphere_hybrid_sigma_pressure_coordinate"
    name_computed = "air_pressure"
    std_p0 = "reference_air_pressure_for_atmosphere_vertical_coordinate"
    std_ps = "surface_air_pressure"

    def select_formula(self, key_mapping):
        if "p0" in key_mapping:
            setattr(self, "__call__", self._a_p0)
        else:
            setattr(self, "__call__", self._ap)

    def _a_p0(self, n, k, j, i):
        return self.a[k] * self.p0 + self.b[k] * self.ps[n, j, i]

    def _ap(self, n, k, j, i):
        return self.ap[k] + self.b[k] * self.ps[n, j, i]

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Atmosphere hybrid height coordinate
# -----------------------------------------------------------------------------
class AtmosphereHybridHeightCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#atmosphere-hybrid-height-coordinate"
    name = "atmosphere_hybrid_height_coordinate"
    name_computed = ("altitude", "height_above_geopotential_datum")
    std_orog = ("surface_altitude", "surface_height_above_geopotential_datum")

    def __call__(self, n, k, j, i):
        return self.a[k] + self.b[k] * self.orog[n, j, i]

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Atmosphere smooth level vertical (SLEVE) coordinate
# -----------------------------------------------------------------------------
class AtmosphereSmoothLevelVerticalCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_atmosphere_smooth_level_vertical_sleve_coordinate"
    name = "atmosphere_sleve_coordinate"
    name_computed = ("altitude", "height_above_geopotential_datum")
    std_ztop = (
        "altitude_at_top_of_atmosphere_model",
        "height_above_geopotential_datum_at_top_of_atmosphere_model",
    )

    def __call__(self, n, k, j, i):
        return (
            self.a[k] * self.ztop
            + self.b1[k] * self.zsurf1[n, j, i]
            + self.b2[k] * self.zsurf2[n, j, i]
        )

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Ocean sigma coordinate
# -----------------------------------------------------------------------------
class OceanSigmaCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_ocean_sigma_coordinate"
    name = "ocean_sigma_coordinate"

    def __call__(self, n, k, j, i):
        return self.eta[n, j, i] + self.sigma[k] * (
            self.depth[j, i] + self.eta[n, j, i]
        )

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Ocean s-coordinate
# -----------------------------------------------------------------------------
class OceanSCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_ocean_s_coordinate"
    name = "ocean_s_coordinate"

    def __call__(self, n, k, j, i):
        c_k = (1 - self.b) * math.sinh(self.a * self.s[k]) / math.sinh(
            self.a
        ) + self.b * [
            math.tanh(self.a * (self.s[k] + 0.5)) / (2 * math.tanh(0.5 * self.a)) - 0.5
        ]
        return (
            self.eta[n, j, i] * (1 + self.s[k])
            + self.depth_c * self.s[k]
            + (self.depth[j, i] - self.depth_c) * c_k
        )

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Ocean s-coordinate, generic form 1
# -----------------------------------------------------------------------------
class OceanSCoordinateGenericForm1(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_ocean_s_coordinate_generic_form_1"
    name = "ocean_s_coordinate_g1"

    def __call__(self, n, k, j, i):
        s_kji = self.depth_c * self.s[k] + (self.depth[j, i] - self.depth_c) * self.C[k]
        return s_kji + self.eta[n, j, i] * (1 + self.S[k, j, i] / self.depth[j, i])

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Ocean s-coordinate, generic form 2
# -----------------------------------------------------------------------------
class OceanSCoordinateGenericForm2(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_ocean_s_coordinate_generic_form_2"
    name = "ocean_s_coordinate_g2"
    std_names = {
        "altitude": {
            "zlev": "altitude",
            "eta": "sea_surface_height_above_geoid",
            "depth": "sea_floor_depth_below_geoid",
        },
        "height_above_geopotential_ datum": {
            "zlev": "height_above_geopotential_datum",
            "eta": "sea_surface_height_above_geopotential_datum",
            "depth": "sea_floor_depth_below_geopotential_datum",
        },
        "height_above_reference_ ellipsoid": {
            "zlev": "height_above_reference_ellipsoid",
            "eta": "sea_surface_height_above_reference_ellipsoid",
            "depth": "sea_floor_depth_below_reference_ellipsoid",
        },
        "height_above_mean_sea_ level": {
            "zlev": "height_above_mean_sea_level",
            "eta": "sea_surface_height_above_mean_ sea_level",
            "depth": "sea_floor_depth_below_mean_ sea_level",
        },
    }

    def __call__(self, n, k, j, i):
        s_kji = (self.depth_c * self.s[k] + self.depth[j, i] * self.C[k]) / (
            self.depth_c + self.depth[j, i]
        )
        return self.eta[n, j, i] + (self.eta[n, j, i] + self.depth[j, i]) * s_kji

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Ocean sigma over z coordinate
# -----------------------------------------------------------------------------
class OceanSigmaOverZCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_ocean_sigma_over_z_coordinate"
    name = "ocean_sigma_z_coordinate"

    def select_formula(self, key_mapping):
        if "sigma" in key_mapping and "zlev" not in key_mapping:
            setattr(self, "__call__", self._sigma)
        elif "zlev" in key_mapping:
            setattr(self, "__call__", self._z_lev)
        else:
            msg = f"No formula for 'ocean_sigma_z_coordinate' with given formula: {key_mapping}"
            raise ValueError(msg)

    def _z_lev(self, n, k, j, i):
        return self.zlev[k]

    def _sigma(self, n, k, j, i):
        return self.eta[n, j, i] + self.sigma[k] * (
            min(self.depth_c, self.depth[j, i]) + self.eta[n, j, i]
        )

    def __len__(self):
        return 4


# -----------------------------------------------------------------------------
# Ocean double sigma coordinate
# -----------------------------------------------------------------------------
class OceanDoubleSigmaCoordinate(AbstractFormula):
    url = f"{CONVENTION_BASE_URL}#_ocean_double_sigma_coordinate"
    name = "ocean_double_sigma_coordinate"

    def __call__(self, k, j, i, **_):
        f_ji = 0.5 * (self.z1 + self.z2) + 0.5 * (self.z1 - self.z2) * math.tanh(
            2 * self.a / (self.z1 - self.z2) * (self.depth[j, i] - self.href)
        )

        if k <= self.k_c:
            return self.sigma[k] * f_ji
        else:
            return f_ji + (self.sigma[k] - 1) * (self.depth[j, i] - f_ji)

    def __len__(self):
        return 3
