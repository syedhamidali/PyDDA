import math
import warnings

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pyart

from .. import retrieval
from matplotlib.axes import Axes

try:
    from cartopy.mpl.geoaxes import GeoAxes

    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False

GeoAxes._pcolormesh_patched = Axes.pcolormesh


def plot_horiz_xsection_streamlines(
    Grids,
    ax=None,
    background_field="reflectivity",
    level=1,
    cmap="ChaseSpectral",
    vmin=None,
    vmax=None,
    u_vel_contours=None,
    v_vel_contours=None,
    w_vel_contours=None,
    wind_vel_contours=None,
    u_field="u",
    v_field="v",
    w_field="w",
    show_lobes=True,
    title_flag=True,
    axes_labels_flag=True,
    colorbar_flag=True,
    colorbar_contour_flag=False,
    bg_grid_no=0,
    contour_alpha=0.7,
    arrowsize=1.0,
    linewidth=None,
):
    """
    This procedure plots a horizontal cross section of winds from wind fields
    generated by PyDDA using streamlines. The density of streamlines varies
    with horizontal wind speed.

    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle
        The axis handle to place the plot on. Set to None to plot on the
        current axis.
    background_field: str
        The name of the background field to plot the windbarbs on.
    level: int
        The number of the vertical level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not
        display such contours.
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not
        display such contours.
    wind_vel_contours: 1-D array
        The contours to use for plotting contours of horizontal wind speed.
        Set to None to not display such contours
    u_field: str
        Name of zonal wind (u) field in Grids.
    v_field: str
        Name of meridional wind (v) field in Grids.
    w_field: str
        Name of vertical wind (w) field in Grids.
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot.
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot background field.
    colorbar_contour_flag: bool
        If True, PyDDA will generate a colorbar for the contours.
    bg_grid_no: int
        Number of grid in Grids to take background field from.
        Set to -1 to use maximum value from all grids.
    contour_alpha: float
        Alpha (transparency) of velocity contours. 0 = transparent, 1 = opaque
    arrowsize: float
        Factor scale arrow size for streamlines.
    linewidth: numeric or 2d array
        Linewidths for streamlines.
    Returns
    -------
    ax: matplotlib axis
        Axis handle to output axis
    """

    grid_bg = Grids[bg_grid_no][background_field].values.squeeze()

    if vmin is None:
        vmin = grid_bg.min()

    if vmax is None:
        vmax = grid_bg.max()

    grid_h = Grids[0]["point_altitude"].values / 1e3
    grid_x = Grids[0]["point_x"].values / 1e3
    grid_y = Grids[0]["point_y"].values / 1e3
    np.diff(grid_x, axis=2)[0, 0, 0]
    np.diff(grid_y, axis=1)[0, 0, 0]
    u = Grids[0][u_field].values.squeeze()
    v = Grids[0][v_field].values.squeeze()
    w = Grids[0][w_field].values.squeeze()

    if isinstance(u, np.ma.MaskedArray):
        u = u.filled(np.nan)

    if isinstance(v, np.ma.MaskedArray):
        v = v.filled(np.nan)

    if isinstance(w, np.ma.MaskedArray):
        w = w.filled(np.nan)

    if ax is None:
        ax = plt.gca()

    the_mesh = ax.pcolormesh(
        grid_x[level, :, :],
        grid_y[level, :, :],
        grid_bg[level, :, :],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )

    np.ma.sqrt(u**2 + v**2)
    ax.streamplot(
        grid_x[level, :, :],
        grid_y[level, :, :],
        u[level, :, :],
        v[level, :, :],
        color="k",
        linewidth=linewidth,
        arrowsize=arrowsize,
    )

    if colorbar_flag is True:
        cp = Grids[bg_grid_no][background_field].attrs["long_name"]
        cp.replace(" ", "_")
        cp = cp + " [" + Grids[bg_grid_no][background_field].attrs["units"]
        cp = cp + "]"
        plt.colorbar(the_mesh, ax=ax, label=(cp))

    if u_vel_contours is not None:
        u_filled = np.ma.filled(u[level, :, :], fill_value=np.nan)
        cs = ax.contour(
            grid_x[level, :, :],
            grid_y[level, :, :],
            u_filled,
            levels=u_vel_contours,
            linewidths=2,
        )
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="U [m/s]")

    if v_vel_contours is not None:
        v_filled = np.ma.filled(v[level, :, :], fill_value=np.nan)
        cs = ax.contour(
            grid_x[level, :, :],
            grid_y[level, :, :],
            v_filled,
            levels=u_vel_contours,
            linewidths=2,
        )
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="V [m/s]")

    if w_vel_contours is not None:
        w_filled = np.ma.filled(w[level, :, :], fill_value=np.nan)
        cs = ax.contour(
            grid_x[level, :, :],
            grid_y[level, :, :],
            w_filled,
            levels=w_vel_contours,
            linewidths=2,
        )
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="W [m/s]")

    if wind_vel_contours is not None:
        vel = np.ma.sqrt(u[level, :, :] ** 2 + v[level, :, :] ** 2)
        # vel = vel.filled(fill_value=np.nan)
        cs = ax.contour(
            grid_x[level, :, :],
            grid_y[level, :, :],
            vel,
            levels=wind_vel_contours,
            linewidths=2,
        )
        cs.set_clim([np.min(wind_vel_contours), np.max(wind_vel_contours)])
        cs.cmap.set_under(color="white", alpha=0)
        cs.cmap.set_bad(color="white", alpha=0)
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="|V| [m/s]")

    bca_min = math.radians(Grids[0][u_field].attrs["min_bca"])
    bca_max = math.radians(Grids[0][u_field].attrs["max_bca"])

    if show_lobes is True:
        for i in range(len(Grids)):
            for j in range(len(Grids)):
                if i != j:
                    bca = retrieval.get_bca(
                        Grids[i],
                        Grids[j],
                    )

                    ax.contour(
                        grid_x[level, :, :],
                        grid_y[level, :, :],
                        bca,
                        levels=[bca_min, bca_max],
                        color="k",
                    )

    if axes_labels_flag is True:
        ax.set_xlabel(("X [km]"))
        ax.set_ylabel(("Y [km]"))

    if title_flag is True:
        ax.set_title(("PyDDA retreived winds @" + str(grid_h[level, 0, 0]) + " km"))

    ax.set_xlim([grid_x.min(), grid_x.max()])
    ax.set_ylim([grid_y.min(), grid_y.max()])
    return ax


def plot_horiz_xsection_streamlines_map(
    Grids,
    ax=None,
    background_field="reflectivity",
    level=1,
    cmap="ChaseSpectral",
    vmin=None,
    vmax=None,
    u_vel_contours=None,
    v_vel_contours=None,
    w_vel_contours=None,
    wind_vel_contours=None,
    u_field="u",
    v_field="v",
    w_field="w",
    show_lobes=True,
    title_flag=True,
    axes_labels_flag=True,
    colorbar_flag=True,
    colorbar_contour_flag=False,
    bg_grid_no=0,
    contour_alpha=0.7,
    coastlines=True,
    gridlines=True,
    arrowsize=1.0,
    linewidth=None,
):
    """
    This procedure plots a horizontal cross section of winds from wind fields
    generated by PyDDA using streamlines. The density of streamlines varies
    with horizontal wind speed.

    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle (with cartopy ccrs)
        The axis handle to place the plot on. Set to None to create a new map.
    Note: the axis needs to be in a PlateCarree() projection.
    background_field: str
        The name of the background field to plot the windbarbs on.
    level: int
        The number of the vertical level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not
        display such contours.
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not
        display such contours.
    wind_vel_contours: 1-D array
        The contours to use for plotting contours of horizontal wind speed.
        Set to None to not display such contours.
    u_field: str
        Name of zonal wind (u) field in Grids.
    v_field: str
        Name of meridional wind (v) field in Grids.
    w_field: str
        Name of vertical wind (w) field in Grids.
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot.
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot background field.
    colorbar_contour_flag: bool
        If True, PyDDA will generate a colorbar for the contours.
    bg_grid_no: int
        Number of grid in Grids to take background field from.
        Set to -1 to use maximum value from all grids.
    contour_alpha: float
        Alpha (transparency) of velocity contours. 0 = transparent, 1 = opaque
    coastlines: bool
        Set to true to display coastlines
    gridlines: bool
        Set to true to show grid lines.
    arrowsize: float
        Factor scale arrow size for streamlines.
    linewidth: numeric or 2d array
        Linewidths for streamlines.

    Returns
    -------
    ax: matplotlib axis
        Axis handle to output axis
    """
    if not CARTOPY_AVAILABLE:
        raise ModuleNotFoundError(
            "Cartopy needs to be installed in order to use plotting module!"
        )

    if bg_grid_no > -1:
        grid_bg = Grids[bg_grid_no][background_field].values.squeeze()
    else:
        grid_array = np.ma.stack([x[background_field].values.squeeze() for x in Grids])
        grid_bg = grid_array.max(axis=0)

    if vmin is None:
        vmin = grid_bg.min()

    if vmax is None:
        vmax = grid_bg.max()

    grid_h = Grids[0]["point_altitude"].values / 1e3
    grid_x = Grids[0]["point_x"].values / 1e3
    grid_y = Grids[0]["point_y"].values / 1e3
    grid_lat = Grids[0].point_latitude["data"][level]
    grid_lon = Grids[0].point_longitude["data"][level]

    np.diff(grid_x, axis=2)[0, 0, 0]
    np.diff(grid_y, axis=1)[0, 0, 0]
    u = Grids[0][u_field].values.squeeze()
    v = Grids[0][v_field].values.squeeze()
    w = Grids[0][w_field].values.squeeze()

    if isinstance(u, np.ma.MaskedArray):
        u = u.filled(np.nan)

    if isinstance(v, np.ma.MaskedArray):
        v = v.filled(np.nan)

    if isinstance(w, np.ma.MaskedArray):
        w = w.filled(np.nan)

    transform = ccrs.PlateCarree()
    if ax is None:
        ax = plt.axes(projection=transform)

    the_mesh = ax.pcolormesh(
        grid_lon[:, :],
        grid_lat[:, :],
        grid_bg[level, :, :],
        cmap=cmap,
        transform=transform,
        zorder=0,
        vmin=vmin,
        vmax=vmax,
    )

    np.ma.sqrt(u**2 + v**2)
    ax.streamplot(
        grid_lon,
        grid_lat,
        u[level],
        v[level],
        transform=transform,
        zorder=1,
        color="k",
        arrowsize=arrowsize,
        linewidth=linewidth,
    )

    if colorbar_flag is True:
        cp = Grids[bg_grid_no][background_field].attrs["long_name"]
        cp.replace(" ", "_")
        cp = cp + " [" + Grids[bg_grid_no][background_field].attrs["units"]
        cp = cp + "]"
        plt.colorbar(the_mesh, ax=ax, label=(cp))

    if u_vel_contours is not None:
        u_filled = np.ma.masked_where(
            u[level, :, :] < np.min(u_vel_contours), u[level, :, :]
        )
        try:
            cs = ax.contourf(
                grid_lon[:, :],
                grid_lat[:, :],
                u_filled,
                levels=u_vel_contours,
                linewidths=2,
                alpha=contour_alpha,
                zorder=2,
                extend="both",
            )
            cs.set_clim([np.min(u_vel_contours), np.max(u_vel_contours)])
            cs.cmap.set_under(color="white", alpha=0)
            cs.cmap.set_over(color="white", alpha=0)
            cs.cmap.set_bad(color="white", alpha=0)
            ax.clabel(cs)
            if colorbar_contour_flag is True:
                plt.colorbar(
                    cs, ax=ax, label="U [m/s]", extend="both", spacing="proportional"
                )
        except ValueError:
            warnings.warn(
                (
                    "Cartopy does not support blank contour plots, "
                    + "contour color map not drawn!"
                ),
                RuntimeWarning,
            )

    if v_vel_contours is not None:
        v_filled = np.ma.masked_where(
            v[level, :, :] < np.min(v_vel_contours), v[level, :, :]
        )
        try:
            cs = ax.contour(
                grid_lon[:, :],
                grid_lat[:, :],
                v_filled,
                levels=u_vel_contours,
                linewidths=2,
                zorder=2,
                extend="both",
            )
            cs.set_clim([np.min(v_vel_contours), np.max(v_vel_contours)])
            cs.cmap.set_under(color="white", alpha=0)
            cs.cmap.set_over(color="white", alpha=0)
            cs.cmap.set_bad(color="white", alpha=0)
            ax.clabel(cs)
            if colorbar_contour_flag is True:
                plt.colorbar(
                    cs, ax=ax, label="V [m/s]", extend="both", spacing="proportional"
                )
        except ValueError:
            warnings.warn(
                (
                    "Cartopy does not support blank contour plots, "
                    + "contour color map not drawn!"
                ),
                RuntimeWarning,
            )

    if w_vel_contours is not None:
        w_filled = np.ma.masked_where(
            w[level, :, :] < np.min(w_vel_contours), w[level, :, :]
        )
        try:
            cs = ax.contour(
                grid_lon[::, ::],
                grid_lat[::, ::],
                w_filled,
                levels=w_vel_contours,
                linewidths=2,
                zorder=2,
                extend="both",
            )
            cs.set_clim([np.min(w_vel_contours), np.max(w_vel_contours)])
            cs.cmap.set_under(color="white", alpha=0)
            cs.cmap.set_over(color="white", alpha=0)
            cs.cmap.set_bad(color="white", alpha=0)
            ax.clabel(cs)
            if colorbar_contour_flag is True:
                plt.colorbar(
                    cs,
                    ax=ax,
                    label="W [m/s]",
                    extend="both",
                    spacing="proportional",
                    ticks=w_vel_contours,
                )
        except ValueError:
            warnings.warn(
                (
                    "Cartopy does not support color maps on blank "
                    + "contour plots, contour color map not drawn!"
                ),
                RuntimeWarning,
            )

    if wind_vel_contours is not None:
        vel = np.ma.sqrt(u[level, :, :] ** 2 + v[level, :, :] ** 2)
        vel = vel.filled(fill_value=np.nan)
        try:
            cs = ax.contour(
                grid_x[level, :, :],
                grid_y[level, :, :],
                vel,
                levels=wind_vel_contours,
                linewidths=2,
            )
            cs.cmap.set_under(color="white", alpha=0)
            cs.cmap.set_bad(color="white", alpha=0)

            ax.clabel(cs)
            if colorbar_contour_flag is True:
                plt.colorbar(
                    cs,
                    ax=ax,
                    label="|V\ [m/s]",
                    extend="both",
                    spacing="proportional",
                    ticks=w_vel_contours,
                )
        except ValueError:
            warnings.warn(
                (
                    "Cartopy does not support color maps on blank "
                    + "contour plots, contour color map not drawn!"
                ),
                RuntimeWarning,
            )

    bca_min = math.radians(Grids[0][u_field].attrs["min_bca"])
    bca_max = math.radians(Grids[0][u_field].attrs["max_bca"])

    if show_lobes is True:
        for i in range(len(Grids)):
            for j in range(len(Grids)):
                if i != j:
                    bca = retrieval.get_bca(Grids[i], Grids[j])

                    ax.contour(
                        grid_lon[:, :],
                        grid_lat[:, :],
                        bca,
                        levels=[bca_min, bca_max],
                        color="k",
                        zorder=1,
                    )

    if axes_labels_flag is True:
        ax.set_xlabel(("Latitude [$^{\circ}$]"))
        ax.set_ylabel(("Longitude [$^{\circ}$]"))

    if title_flag is True:
        ax.set_title(("PyDDA retreived winds @" + str(grid_h[level, 0, 0]) + " km"))

    if coastlines is True:
        ax.coastlines(resolution="10m")

    if gridlines is True:
        ax.gridlines()

    ax.set_extent([grid_lon.min(), grid_lon.max(), grid_lat.min(), grid_lat.max()])
    num_tenths = int(round((grid_lon.max() - grid_lon.min()) * 10) + 1)
    the_ticks_x = np.round(np.linspace(grid_lon.min(), grid_lon.max(), num_tenths), 1)
    num_tenths = int(round((grid_lat.max() - grid_lat.min()) * 10) + 1)
    the_ticks_y = np.round(np.linspace(grid_lat.min(), grid_lat.max(), num_tenths), 1)
    ax.set_xticks(the_ticks_x)
    ax.set_yticks(the_ticks_y)
    return ax


def plot_xz_xsection_streamlines(
    Grids,
    ax=None,
    background_field="reflectivity",
    level=1,
    cmap="ChaseSpectral",
    vmin=None,
    vmax=None,
    u_vel_contours=None,
    v_vel_contours=None,
    w_vel_contours=None,
    wind_vel_contours=None,
    u_field="u",
    v_field="v",
    w_field="w",
    title_flag=True,
    axes_labels_flag=True,
    colorbar_flag=True,
    colorbar_contour_flag=False,
    bg_grid_no=0,
    contour_alpha=0.7,
    arrowsize=1.0,
    linewidth=None,
):
    """
    This procedure plots a cross section of winds from wind fields
    generated by PyDDA in the X-Z plane using streamlines.
    The density of streamlines varies with horizontal wind speed.

    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle
        The axis handle to place the plot on. Set to None to plot on the
        current axis.
    background_field: str
        The name of the background field to plot the streamlines on.
    level: int
        The number of the Y level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not
        display such contours.
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not
        display such contours.
    wind_vel_contours: 1-D array
        The contours to use for plotting contours of horizontal wind speed.
        Set to None to not display such contours.
    u_field: str
        Name of zonal wind (u) field in Grids.
    v_field: str
        Name of meridional wind (v) field in Grids.
    w_field: str
        Name of vertical wind (w) field in Grids.
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot background field.
    colorbar_contour_flag: bool
        If True, PyDDA will generate a colorbar for the contours.
    bg_grid_no: int
        Number of grid in Grids to take background field from.
        Set to -1 to use maximum value from all grids.
    contour_alpha: float
        Alpha (transparency) of velocity contours. 0 = transparent, 1 = opaque
    arrowsize: float
        Factor scale arrow size for streamlines.
    linewidth: numeric or 2d array
        Linewidths for streamlines.

    Returns
    -------
    ax: matplotlib axis
        Axis handle to output axis
    """

    grid_bg = Grids[bg_grid_no][background_field].values.squeeze()

    if vmin is None:
        vmin = grid_bg.min()

    if vmax is None:
        vmax = grid_bg.max()

    grid_h = Grids[0]["point_altitude"].values / 1e3
    grid_x = Grids[0]["point_x"].values / 1e3
    grid_y = Grids[0]["point_y"].values / 1e3
    u = Grids[0][u_field].values.squeeze()
    v = Grids[0][v_field].values.squeeze()
    w = Grids[0][w_field].values.squeeze()

    if isinstance(u, np.ma.MaskedArray):
        u = u.filled(np.nan)

    if isinstance(v, np.ma.MaskedArray):
        v = v.filled(np.nan)

    if isinstance(w, np.ma.MaskedArray):
        w = w.filled(np.nan)

    if ax is None:
        ax = plt.gca()

    the_mesh = ax.pcolormesh(
        grid_x[:, level, :],
        grid_h[:, level, :],
        grid_bg[:, level, :],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )

    ax.streamplot(
        grid_x[:, level, :],
        grid_h[:, level, :],
        u[:, level, :],
        w[:, level, :],
        color="k",
        arrowsize=arrowsize,
        linewidth=linewidth,
    )

    if colorbar_flag is True:
        cp = Grids[bg_grid_no][background_field].attrs["long_name"]
        cp.replace(" ", "_")
        cp = cp + " [" + Grids[bg_grid_no][background_field].attrs["units"]
        cp = cp + "]"
        plt.colorbar(the_mesh, ax=ax, label=(cp))

    if u_vel_contours is not None:
        u_filled = np.ma.filled(u[:, level, :], fill_value=np.nan)
        cs = ax.contour(
            grid_x[:, level, :],
            grid_h[:, level, :],
            u_filled,
            levels=u_vel_contours,
            linewidths=2,
        )
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="U [m/s]")

    if v_vel_contours is not None:
        v_filled = np.ma.filled(w[:, level, :], fill_value=np.nan)
        cs = ax.contour(
            grid_x[:, level, :],
            grid_h[:, level, :],
            v_filled,
            levels=v_vel_contours,
            linewidths=2,
        )
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="V [m/s]")

    if w_vel_contours is not None:
        w_filled = np.ma.filled(w[:, level, :], fill_value=np.nan)
        cs = ax.contour(
            grid_x[:, level, :],
            grid_h[:, level, :],
            w_filled,
            levels=w_vel_contours,
            linewidths=2,
        )
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="W [m/s]")

    if wind_vel_contours is not None:
        vel = np.ma.sqrt(u[:, level, :] ** 2 + v[:, level, :] ** 2)
        vel = vel.filled(fill_value=np.nan)
        cs = ax.contour(
            grid_x[:, level, :],
            grid_h[:, level, :],
            vel,
            levels=wind_vel_contours,
            linewidths=2,
        )
        cs.set_clim([np.min(wind_vel_contours), np.max(wind_vel_contours)])
        cs.cmap.set_under(color="white", alpha=0)
        cs.cmap.set_bad(color="white", alpha=0)
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="|V| [m/s]")

    if axes_labels_flag is True:
        ax.set_xlabel(("X [km]"))
        ax.set_ylabel(("Z [km]"))

    if title_flag is True:
        if grid_y[0, level, 0] > 0:
            ax.set_title(
                (
                    "PyDDA retreived winds @"
                    + str(grid_y[0, level, 0])
                    + " km north of origin."
                )
            )
        else:
            ax.set_title(
                (
                    "PyDDA retreived winds @"
                    + str(-grid_y[0, level, 0])
                    + " km south of origin."
                )
            )

    ax.set_xlim([grid_x.min(), grid_x.max()])
    ax.set_ylim([grid_h.min(), grid_h.max()])
    return ax


def plot_yz_xsection_streamlines(
    Grids,
    ax=None,
    background_field="reflectivity",
    level=1,
    cmap="ChaseSpectral",
    vmin=None,
    vmax=None,
    u_vel_contours=None,
    v_vel_contours=None,
    w_vel_contours=None,
    wind_vel_contours=None,
    u_field="u",
    v_field="v",
    w_field="w",
    title_flag=True,
    axes_labels_flag=True,
    colorbar_flag=True,
    colorbar_contour_flag=False,
    bg_grid_no=0,
    contour_alpha=0.7,
    arrowsize=1.0,
    linewidth=None,
):
    """
    This procedure plots a cross section of winds from wind fields
    generated by PyDDA in the Y-Z plane using streamlines.
    The density of streamlines varies with horizontal wind speed.

    Parameters
    ----------
    Grids: list
        List of Py-ART Grids to visualize
    ax: matplotlib axis handle
        The axis handle to place the plot on. Set to None to plot on the
        current axis.
    background_field: str
        The name of the background field to plot the streamlines on.
    level: int
        The number of the X level to plot the cross section through.
    cmap: str or matplotlib colormap
        The name of the matplotlib colormap to use for the background field.
    vmin: float
        The minimum bound to use for plotting the background field. None will
        automatically detect the background field minimum.
    vmax: float
        The maximum bound to use for plotting the background field. None will
        automatically detect the background field maximum.
    u_vel_contours: 1-D array
        The contours to use for plotting contours of u. Set to None to not
        display such contours.
    v_vel_contours: 1-D array
        The contours to use for plotting contours of v. Set to None to not
        display such contours.
    w_vel_contours: 1-D array
        The contours to use for plotting contours of w. Set to None to not
        display such contours.
    wind_vel_contours: 1-D aray
        The contours to use for plotting contours of horizontal wind speed.
        Set to None to not display such contours.
    u_field: str
        Name of zonal wind (u) field in Grids.
    v_field: str
        Name of meridional wind (v) field in Grids.
    w_field: str
        Name of vertical wind (w) field in Grids.
    show_lobes: bool
        If True, the dual doppler lobes from each pair of radars will be shown.
    title_flag: bool
        If True, PyDDA will generate a title for the plot.
    axes_labels_flag: bool
        If True, PyDDA will generate axes labels for the plot.
    colorbar_flag: bool
        If True, PyDDA will generate a colorbar for the plot background field.
    colorbar_contour_flag: bool
        If True, PyDDA will generate a colorbar for the contours.
    bg_grid_no: int
        Number of grid in Grids to take background field from.
        Set to -1 to use maximum value from all grids.
    contour_alpha: float
        Alpha (transparency) of velocity contours. 0 = transparent, 1 = opaque
    arrowsize: float
        Factor scale arrow size for streamlines.
    linewidth: numeric or 2d array
        Linewidths for streamlines.

    Returns
    -------
    ax: Matplotlib axis handle
        The matplotlib axis handle corresponding to the plot
    """

    grid_bg = Grids[bg_grid_no][background_field].values.squeeze()
    if vmin is None:
        vmin = grid_bg.min()

    if vmax is None:
        vmax = grid_bg.max()

    grid_h = Grids[0]["point_altitude"].values / 1e3
    grid_x = Grids[0]["point_x"].values / 1e3
    grid_y = Grids[0]["point_y"].values / 1e3
    np.diff(grid_x, axis=2)[0, 0, 0]
    np.diff(grid_y, axis=1)[0, 0, 0]
    u = Grids[0][u_field].values.squeeze()
    v = Grids[0][v_field].values.squeeze()
    w = Grids[0][w_field].values.squeeze()

    if isinstance(u, np.ma.MaskedArray):
        u = u.filled(np.nan)

    if isinstance(v, np.ma.MaskedArray):
        v = v.filled(np.nan)

    if isinstance(w, np.ma.MaskedArray):
        w = w.filled(np.nan)

    if ax is None:
        ax = plt.gca()

    the_mesh = ax.pcolormesh(
        grid_y[:, :, level],
        grid_h[:, :, level],
        grid_bg[:, :, level],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )

    ax.streamplot(
        grid_y[:, :, level],
        grid_h[:, :, level],
        v[:, :, level],
        w[:, :, level],
        color="k",
        cmap="coolwarm",
        arrowsize=arrowsize,
        linewidth=linewidth,
    )

    if colorbar_flag is True:
        cp = Grids[bg_grid_no][background_field].attrs["long_name"]
        cp.replace(" ", "_")
        cp = cp + " [" + Grids[bg_grid_no][background_field].attrs["units"]
        cp = cp + "]"
        plt.colorbar(the_mesh, ax=ax, label=(cp))

    if u_vel_contours is not None:
        u_filled = np.ma.filled(u[:, :, level], fill_value=np.nan)
        cs = ax.contour(
            grid_y[:, :, level], grid_h[:, :, level], u_filled, levels=u_vel_contours
        )
        plt.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="U [m/s]")

    if v_vel_contours is not None:
        v_filled = np.ma.filled(v[:, :, level], fill_value=np.nan)
        cs = ax.contour(
            grid_y[:, :, level], grid_h[:, :, level], v_filled, levels=w_vel_contours
        )
        plt.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="V [m/s]")

    if w_vel_contours is not None:
        w_filled = np.ma.filled(w[:, :, level], fill_value=np.nan)
        cs = ax.contour(
            grid_y[:, :, level],
            grid_h[:, :, level],
            w_filled,
            levels=w_vel_contours,
            linewidths=2,
        )
        plt.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="W [m/s]")

    if wind_vel_contours is not None:
        vel = np.ma.sqrt(u[:, :, level] ** 2 + v[:, :, level] ** 2)
        vel = vel.filled(fill_value=np.nan)
        cs = ax.contour(
            grid_y[:, :, level],
            grid_h[:, :, level],
            vel,
            levels=wind_vel_contours,
            linewidths=2,
            alpha=contour_alpha,
        )
        cs.set_clim([np.min(wind_vel_contours), np.max(wind_vel_contours)])
        cs.cmap.set_under(color="white", alpha=0)
        cs.cmap.set_bad(color="white", alpha=0)
        ax.clabel(cs)
        if colorbar_contour_flag is True:
            plt.colorbar(cs, ax=ax, label="|V| [m/s]")

    if axes_labels_flag is True:
        ax.set_xlabel(("Y [km]"))
        ax.set_ylabel(("Z [km]"))

    if title_flag is True:
        if grid_x[0, 0, level] > 0:
            ax.set_title(
                (
                    "PyDDA retreived winds @"
                    + str(grid_x[0, level, 0])
                    + " km east of origin."
                )
            )
        else:
            ax.set_title(
                (
                    "PyDDA retreived winds @"
                    + str(-grid_x[0, level, 0])
                    + " km west of origin."
                )
            )

    ax.set_xlim([grid_y.min(), grid_y.max()])
    ax.set_ylim([grid_h.min(), grid_h.max()])
    return ax
