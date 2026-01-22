import json

import folium
from folium.plugins import AntPath, BeautifyIcon, Fullscreen

from utils.coord_transform import bd09_to_wgs84

COLOR_PICKUP = "#52c41a"  # 绿色
COLOR_DELIVERY = "#fa8c16"  # 橙色
COLOR_DEPOT = "#d9534f"  # 红色
COLOR_VEHICLE = "#0275d8"  # 蓝色


class MapTemplate:
    """管理所有地图弹窗的 HTML/CSS 模板"""

    @staticmethod
    def get_base_style():
        return """
        <style>
            .map-popup { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 240px; color: #333; padding: 5px; }
            .map-header { border-bottom: 2px solid #f0f0f0; margin-bottom: 10px; padding-bottom: 5px; }
            .map-header h3 { margin: 0; font-size: 16px; font-weight: 600; display: flex; align-items: center; }
            .info-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; border-bottom: 1px solid #fafafa; }
            .info-label { color: #666; font-weight: 500; }
            .info-value { color: #111; font-weight: 600; text-align: right; }
            .divider { margin: 10px 0; border-top: 1px dashed #eee; }
            .status-tag { padding: 2px 8px; border-radius: 10px; font-size: 11px; color: white; background: #888; }
            .reason-box { background: #fff1f0; border: 1px solid #ffa39e; padding: 8px; border-radius: 4px; margin-top: 8px; font-size: 12px; color: #cf1322; }
        </style>
        """

    @classmethod
    def render_depot(cls, depot):
        return f"""
        {cls.get_base_style()}
        <div class="map-popup">
            <div class="map-header"><h3 style="color: #d9534f;">🏠 仓库信息</h3></div>
            <div class="info-row"><span class="info-label">名称:</span><span class="info-value">{depot['station_name']}</span></div>
            <div class="info-row"><span class="info-label">ID:</span><span class="info-value">{depot['station_id']}</span></div>
            <div class="info-row"><span class="info-label">区域:</span><span class="info-value">{depot.get('area', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">详细地址:</span><span class="info-value">{depot.get('location', 'N/A')}</span></div>
        </div>
        """

    @classmethod
    def render_vehicle(cls, v):
        return f"""
        {cls.get_base_style()}
        <div class="map-popup">
            <div class="map-header"><h3 style="color: #0275d8;">🚚 车辆信息</h3></div>
            <div class="info-row"><span class="info-label">车牌:</span><span class="info-value">{v['vehicle_id']}</span></div>
            <div class="info-row"><span class="info-label">类型:</span><span class="info-value">{v['vehicle_type']}</span></div>
            <div class="info-row"><span class="info-label">载重能力:</span><span class="info-value">{v['current_load']} / {v['capacity']} 箱</span></div>
            <div class="info-row"><span class="info-label">工作时间:</span><span class="info-value">{v['work_hours']['start']} - {v['work_hours']['end']}</span></div>
            <div class="divider"></div>
            <div class="info-row"><span class="info-label">运行状态:</span><span class="status-tag" style="background:#0275d8">{v['vehicle_status']}</span></div>
        </div>
        """

    @classmethod
    def render_station(
        cls, st, stop_info=None, unassigned_reason=None, new_demand=None
    ):
        """通用站点模板：支持基础地图、已指派路径图、未指派图"""
        d_val = st.get("demands", 0)
        d_color = "#52c41a" if d_val >= 0 else "#fa8c16"
        icon = "📈" if d_val >= 0 else "📉"

        # 基础 HTML 结构
        html = f"""
        {cls.get_base_style()}
        <div class="map-popup">
            <div class="map-header"><h3 style="color: {d_color};">{icon} {st.get('station_name', '未知站点')}</h3></div>
            <div class="info-row"><span class="info-label">ID:</span><span class="info-value">{st.get('station_id', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">详细地址:</span><span class="info-value">{st.get('location', st.get('address', 'N/A'))}</span></div>
            <div class="info-row"><span class="info-label">区域:</span><span class="info-value">{st.get('area', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">需求量:</span><span class="info-value" style="color:{d_color}">{d_val:+} 箱</span></div>
        """

        # --- 新增：如果传了 new_demand，就显示出来 ---
        if new_demand is not None:
            nd_text = f"{new_demand:+}" if new_demand >= 0 else str(new_demand)
            html += f"""<div class="info-row"><span class="info-label" style="color:#096dd9;">新需求:</span><span class="info-value" style="color:#096dd9; font-weight:bold;">{nd_text} 箱</span></div>"""
        # ----------------------------------------

        html += f"""
            <div class="info-row"><span class="info-label">锁柜(空闲/总数):</span><span class="info-value">{st.get('available_nums', 0)}/{st.get('locker_nums', 0)}</span></div>
            <div class="info-row"><span class="info-label">服务耗时:</span><span class="info-value">{st.get('service_time', 0)} min</span></div>
            <div class="info-row"><span class="info-label">优先级:</span><span class="info-value">{st.get('priority', 0)}</span></div>
            <div class="info-row"><span class="info-label">需求时间:</span><span class="info-value" style="font-size:11px;">{st.get('demand_time', 'N/A')}</span></div>
            <div class="info-row"><span class="info-label">原始坐标:</span><span class="info-value">{st.get('longitude')}, {st.get('latitude')}</span></div>
        """

        if stop_info:
            html += f"""
            <div class="divider"></div>
            <div class="info-row" style="color:#096dd9;"><span class="info-label">配送顺序:</span><span class="info-value">第 {stop_info['index']} 站</span></div>
            <div class="info-row"><span class="info-label">预计到达:</span><span class="info-value">{stop_info['arrival_time']}</span></div>
            <div class="info-row"><span class="info-label">服务后负载:</span><span class="info-value">{stop_info['load_after_service']} 箱</span></div>
            """

        if unassigned_reason:
            html += f"""<div class="reason-box"><strong>未指派原因:</strong><br>{unassigned_reason}</div>"""

        html += "</div>"
        return html


def create_visualization(data_file="data/req.json", output_file="input_map.html"):
    """
    [升级版] 创建基础物流分布图
    风格已与 create_output_visualization 统一，使用 BeautifyIcon 和 图层控制
    """
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. 地图初始化
    depot_wgs = bd09_to_wgs84(data["depot"]["longitude"], data["depot"]["latitude"])
    m = folium.Map(location=depot_wgs, zoom_start=14, tiles="CartoDB positron")
    Fullscreen().add_to(m)

    # 2. 定义图层 (FeatureGroup) - 模仿第二个函数的图层管理
    layer_base = folium.FeatureGroup(name="🏢 基础设置 (仓库/车辆)", show=True)
    layer_pickup = folium.FeatureGroup(name="🟩 取货需求点 (Pickup)", show=True)
    layer_delivery = folium.FeatureGroup(name="🟧 送货需求点 (Delivery)", show=True)

    # 将图层添加到地图
    layer_base.add_to(m)
    layer_pickup.add_to(m)
    layer_delivery.add_to(m)

    # 3. 绘制仓库 (加入基础图层)
    folium.Marker(
        depot_wgs,
        popup=folium.Popup(MapTemplate.render_depot(data["depot"]), max_width=350),
        icon=folium.Icon(color="red", icon="home", prefix="fa"),
    ).add_to(layer_base)

    # 4. 绘制车辆 (加入基础图层)
    vehicle_wgs = bd09_to_wgs84(
        data["vehicle"]["longitude"], data["vehicle"]["latitude"]
    )
    folium.Marker(
        vehicle_wgs,
        popup=folium.Popup(MapTemplate.render_vehicle(data["vehicle"]), max_width=350),
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
    ).add_to(layer_base)

    # 5. 绘制站点 - 使用 BeautifyIcon 替代 CircleMarker
    for st in data["stations"]:
        st_wgs = bd09_to_wgs84(st["longitude"], st["latitude"])
        popup_content = MapTemplate.render_station(st)

        # 判断类型
        is_pickup = st["demands"] >= 0
        color = COLOR_PICKUP if is_pickup else COLOR_DELIVERY
        target_layer = layer_pickup if is_pickup else layer_delivery

        # 使用与 output_map 相同风格的图标，但 icon 改为 'cube' 表示货物
        icon = BeautifyIcon(
            icon="cube",  # 盒子图标，表示这是一个任务点
            icon_shape="circle",  # 圆形底座
            background_color=color,
            text_color="white",
            border_color="white",
            prefix="fa",  # FontAwesome
        )

        folium.Marker(
            location=st_wgs, popup=folium.Popup(popup_content, max_width=350), icon=icon
        ).add_to(target_layer)

    # 6. 添加图层控制器
    folium.LayerControl(collapsed=False).add_to(m)

    m.save(output_file)
    print(f"✅ 基础分布地图已生成 (样式已统一): {output_file}")


def create_output_visualization(
    req_file="data/req.json",
    response_file="data/response.json",
    output_file="output_map.html",
):
    with open(req_file, "r", encoding="utf-8") as f:
        req_data = json.load(f)
    with open(response_file, "r", encoding="utf-8") as f:
        response_data = json.load(f)

    # 地图初始化
    depot_wgs = bd09_to_wgs84(
        req_data["depot"]["longitude"], req_data["depot"]["latitude"]
    )
    m = folium.Map(location=depot_wgs, zoom_start=14, tiles="CartoDB positron")
    Fullscreen().add_to(m)

    # 图层定义
    assigned_group = folium.FeatureGroup(name="✅ 已指派路线").add_to(m)
    reason_colors = {
        "为优化总成本而被放弃 (惩罚项生效)": "#dc3545",
        "预剪枝: 需求为零的站点": "#fd7e14",
        "预剪枝: 未启用储车区": "#6f42c1",
        "other": "#6c757d",
    }
    unassigned_layers = {
        r: folium.FeatureGroup(name=f"❌ 未指派 - {r}").add_to(m) for r in reason_colors
    }

    # 2. 绘制车辆起步点
    vehicle_wgs = bd09_to_wgs84(
        req_data["vehicle"]["longitude"], req_data["vehicle"]["latitude"]
    )
    folium.Marker(
        vehicle_wgs,
        popup=folium.Popup(
            MapTemplate.render_vehicle(req_data["vehicle"]), max_width=350
        ),
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
    ).add_to(assigned_group)

    # 3. 准备数据映射
    station_map = {s["station_id"]: s for s in req_data["stations"]}
    route_coords = [vehicle_wgs]

    # 4. 绘制已指派站点
    stop_idx = 1
    for route in response_data["data"]["routes"]:
        for stop in route["stops"]:
            sid = stop["location_id"]
            if sid in station_map:
                st = station_map[sid]
                st_wgs = bd09_to_wgs84(st["longitude"], st["latitude"])
                route_coords.append(st_wgs)

                # 使用模板渲染 Popup
                popup_content = MapTemplate.render_station(
                    st,
                    stop_info={
                        "index": stop_idx,
                        "arrival_time": stop["arrival_time"],
                        "load_after_service": stop["load_after_service"],
                    },
                    new_demand=stop.get("demand", 0),
                )

                # 绘制 Marker
                folium.Marker(
                    location=st_wgs,
                    popup=folium.Popup(popup_content, max_width=350),
                    icon=BeautifyIcon(
                        icon_shape="circle",
                        number=stop_idx,
                        background_color="#52c41a" if st["demands"] >= 0 else "#fa8c16",
                        text_color="white",
                        border_color="white",
                    ),
                ).add_to(assigned_group)
                stop_idx += 1

    # 5. 绘制动态路径
    if len(route_coords) > 1:
        AntPath(locations=route_coords, delay=1000, color="#007bff", weight=5).add_to(
            assigned_group
        )

    # 6. 绘制未指派站点
    for un in response_data["data"]["unassigned_tasks"]:
        sid = un["location_id"]
        if sid in station_map:
            st = station_map[sid]
            st_wgs = bd09_to_wgs84(st["longitude"], st["latitude"])
            reason = un.get("reason", "other")
            target_group = unassigned_layers.get(reason, unassigned_layers["other"])

            popup_content = MapTemplate.render_station(
                st, unassigned_reason=un["reason"]
            )

            folium.CircleMarker(
                location=st_wgs,
                radius=7,
                fill=True,
                color=reason_colors.get(reason, "#6c757d"),
                popup=folium.Popup(popup_content, max_width=350),
            ).add_to(target_group)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(output_file)
    print(f"✨ 可视化地图已生成: {output_file}")


if __name__ == "__main__":
    # 假设 data/ 目录下已有相关文件
    create_visualization()
    create_output_visualization()
