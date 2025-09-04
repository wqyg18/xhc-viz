import math

# ===== 坐标转换函数 (BD-09 -> WGS84) =====
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323

def bd09_to_gcj02(bd_lon, bd_lat):
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lon = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return gg_lon, gg_lat

def gcj02_to_wgs84(lon, lat):
    def out_of_china(lon, lat):
        return not (73.66 < lon < 135.05 and 3.86 < lat < 53.55)

    def transformlat(lon, lat):
        ret = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lon * lat + 0.2 * math.sqrt(abs(lon))
        ret += (20.0 * math.sin(6.0 * lon * pi) + 20.0 *
                math.sin(2.0 * lon * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * pi) + 40.0 *
                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return ret

    def transformlon(lon, lat):
        ret = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + \
              0.1 * lon * lat + 0.1 * math.sqrt(abs(lon))
        ret += (20.0 * math.sin(6.0 * lon * pi) + 20.0 *
                math.sin(2.0 * lon * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lon * pi) + 40.0 *
                math.sin(lon / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lon / 12.0 * pi) + 300.0 *
                math.sin(lon / 30.0 * pi)) * 2.0 / 3.0
        return ret

    if out_of_china(lon, lat):
        return lon, lat
    dlat = transformlat(lon - 105.0, lat - 35.0)
    dlon = transformlon(lon - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) /
           (magic * sqrtmagic) * pi)
    dlon = (dlon * 180.0) / (a / sqrtmagic *
           math.cos(radlat) * pi)
    mglat = lat + dlat
    mglon = lon + dlon
    return lat * 2 - mglat, lon * 2 - mglon

def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)