import json

import folium
from folium.features import DivIcon
from folium.plugins import AntPath, BeautifyIcon

from utils.coord_transform import bd09_to_wgs84

# TODO: 输入req可能没有depot
def create_visualization(data_file="data/req.json", output_file="input_map.html"):
    """
    创建物流可视化地图

    Args:
        data_file: 输入数据文件路径
        output_file: 输出HTML文件路径
    """
    # ===== 读取 JSON 文件 =====
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 中心点用仓库
    depot_wgs = bd09_to_wgs84(data["depot"]["longitude"], data["depot"]["latitude"])
    m = folium.Map(location=depot_wgs, zoom_start=14, tiles="CartoDB positron")

    # 仓库
    folium.Marker(
        depot_wgs,
        popup=folium.Popup(
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 300px;">
                <h3 style="color: #d9534f; margin: 0 0 10px 0;">仓库信息</h3>
                <p><strong>名称:</strong> {data['depot']['station_name']}</p>
                <p><strong>ID:</strong> {data['depot']['station_id']}</p>
                <p><strong>地址:</strong> {data['depot']['location']}</p>
                <p><strong>区域:</strong> {data['depot']['area']}</p>
                <p><strong>坐标:</strong> {data['depot']['longitude']:.6f}, {data['depot']['latitude']:.6f}</p>
            </div>
            """,
            max_width=300,
        ),
        icon=folium.Icon(color="red", icon="home", prefix="fa"),
    ).add_to(m)

    # 车辆
    vehicle_wgs = bd09_to_wgs84(
        data["vehicle"]["longitude"], data["vehicle"]["latitude"]
    )
    folium.Marker(
        vehicle_wgs,
        popup=folium.Popup(
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 300px;">
                <h3 style="color: #0275d8; margin: 0 0 10px 0;">车辆信息</h3>
                <p><strong>车牌:</strong> {data['vehicle']['vehicle_id']}</p>
                <p><strong>当前位置:</strong> {data['vehicle']['location']}</p>
                <p><strong>区域:</strong> {data['vehicle']['current_area']}</p>
                <p><strong>类型:</strong> {data['vehicle']['vehicle_type']}</p>
                <p><strong>容量:</strong> {data['vehicle']['capacity']} 箱</p>
                <p><strong>当前负载:</strong> {data['vehicle']['current_load']} 箱</p>
                <p><strong>状态:</strong> {data['vehicle']['vehicle_status']}</p>
                <p><strong>今日剩余任务:</strong> {data['vehicle']['remaining_tasks_today']}</p>
                <p><strong>工作时间:</strong> {data['vehicle']['work_hours']['start']} - {data['vehicle']['work_hours']['end']}</p>
            </div>
            """,
            max_width=300,
        ),
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
    ).add_to(m)

    # 各个站点
    for st in data["stations"]:
        st_wgs = bd09_to_wgs84(st["longitude"], st["latitude"])

        # 格式化需求信息
        demand_text = f"+{st['demands']}" if st["demands"] >= 0 else str(st["demands"])
        demand_color = "#5cb85c" if st["demands"] >= 0 else "#f0ad4e"

        folium.CircleMarker(
            st_wgs,
            radius=6,
            popup=folium.Popup(
                f"""
                <div style="font-family: Arial, sans-serif; max-width: 300px;">
                    <h3 style="color: {demand_color}; margin: 0 0 10px 0;">站点信息</h3>
                    <p><strong>名称:</strong> {st['station_name']}</p>
                    <p><strong>ID:</strong> {st['station_id']}</p>
                    <p><strong>地址:</strong> {st['location'] if st['location'] else '未知'}</p>
                    <p><strong>区域:</strong> {st['area']}</p>
                    <p><strong style="color: {demand_color};">需求:</strong> {demand_text} 箱</p>
                    <p><strong>锁柜总数:</strong> {st['locker_nums']}</p>
                    <p><strong>可用锁柜:</strong> {st['available_nums']}</p>
                    <p><strong>服务时间:</strong> {st['service_time']} 分钟</p>
                    <p><strong>优先级:</strong> {st['priority']}</p>
                    <p><strong>需求时间:</strong> {st['demand_time']}</p>
                    <p><strong>坐标:</strong> {st['longitude']:.6f}, {st['latitude']:.6f}</p>
                </div>
                """,
                max_width=300,
            ),
            color="green" if st["demands"] >= 0 else "orange",
            fill=True,
            fill_opacity=0.7,
        ).add_to(m)

    # 保存地图
    m.save(output_file)


def create_output_visualization(
    req_file="data/req.json",
    response_file="data/response.json",
    output_file="output_map.html",
):
    """
    创建美化且动态的输出结果可视化地图（已修正点击问题）

    Args:
        req_file: 请求数据文件路径
        response_file: 响应数据文件路径
        output_file: 输出HTML文件路径
    """
    # ===== 读取 JSON 文件 =====
    with open(req_file, "r", encoding="utf-8") as f:
        req_data = json.load(f)

    with open(response_file, "r", encoding="utf-8") as f:
        response_data = json.load(f)

    # 中心点用仓库
    depot_wgs = bd09_to_wgs84(
        req_data["depot"]["longitude"], req_data["depot"]["latitude"]
    )
    m = folium.Map(location=depot_wgs, zoom_start=14, tiles="CartoDB positron")

    # ===== 创建图层组，用于图层控制 =====
    assigned_route_group = folium.FeatureGroup(
        name="已指派路线 (Assigned Route)"
    ).add_to(m)
    
    # 创建按未指派原因分组的图层组
    unassigned_groups = {}
    reason_colors = {
        "为优化总成本而被放弃 (惩罚项生效)": "#dc3545",  # 红色 - 成本优化放弃
        "预剪枝: 需求为零的站点": "#fd7e14",  # 橙色 - 需求为零
        "预剪枝: 未启用储车区": "#6f42c1",  # 紫色 - 未启用储车区
        "other": "#6c757d"  # 灰色 - 其他原因
    }
    
    # 为每种原因创建图层组
    for reason, color in reason_colors.items():
        group_name = f"未指派站点 - {reason}"
        unassigned_groups[reason] = folium.FeatureGroup(name=group_name).add_to(m)

    # 仓库
    folium.Marker(
        depot_wgs,
        popup=folium.Popup(
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 300px;">
                <h3 style="color: #d9534f; margin: 0 0 10px 0;">仓库信息</h3>
                <p><strong>名称:</strong> {req_data['depot']['station_name']}</p>
                <p><strong>ID:</strong> {req_data['depot']['station_id']}</p>
                <p><strong>地址:</strong> {req_data['depot']['location']}</p>
            </div>
            """,
            max_width=300,
        ),
        icon=folium.Icon(color="red", icon="home", prefix="fa"),
    ).add_to(m)

    # 车辆
    vehicle_wgs = bd09_to_wgs84(
        req_data["vehicle"]["longitude"], req_data["vehicle"]["latitude"]
    )
    folium.Marker(
        vehicle_wgs,
        popup=folium.Popup(
            f"""
            <div style="font-family: Arial, sans-serif; max-width: 300px;">
                <h3 style="color: #0275d8; margin: 0 0 10px 0;">车辆信息</h3>
                <p><strong>车牌:</strong> {req_data['vehicle']['vehicle_id']}</p>
                <p><strong>当前位置:</strong> {req_data['vehicle']['location']}</p>
            </div>
            """,
            max_width=300,
        ),
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
    ).add_to(assigned_route_group)

    # 创建站点ID映射
    station_id_map = {}
    for station in req_data["stations"]:
        station_id_map[station["station_id"]] = station

    # 绘制已指派站点的路线
    route_coordinates = [vehicle_wgs]
    stop_counter = 1
    for route in response_data["data"]["routes"]:
        for stop in route["stops"]:
            location_id = stop["location_id"]
            if location_id in station_id_map:
                station = station_id_map[location_id]
                st_wgs = bd09_to_wgs84(station["longitude"], station["latitude"])
                route_coordinates.append(st_wgs)

                demand_text = (
                    f"+{station['demands']}"
                    if station["demands"] >= 0
                    else str(station["demands"])
                )
                serviced_demand = stop.get("demand", 0) 
                new_demand_text = (
                    f"+{serviced_demand}"
                    if serviced_demand >= 0
                    else str(serviced_demand)
                )
                demand_color = "#5cb85c" if station["demands"] >= 0 else "#f0ad4e"

                # 2. 【核心修改】使用 BeautifyIcon 将数字和标记合并
                icon = BeautifyIcon(
                    icon_shape="circle",
                    number=stop_counter,
                    spin=False,
                    border_color=demand_color,
                    background_color=demand_color,
                    text_color="#FFFFFF",
                    inner_icon_style="font-size:12px;padding-top:2px;",
                )

                folium.Marker(
                    location=st_wgs,
                    popup=folium.Popup(
                        f"""
                        <div style="font-family: Arial, sans-serif; max-width: 300px;">
                            <h3 style="color: {demand_color}; margin: 0 0 10px 0;">站点信息 (顺序: {stop_counter})</h3>
                            <p><strong>名称:</strong> {station['station_name']}</p>
                            <p><strong>ID:</strong> {station['station_id']}</p>
                            <p><strong style="color: {demand_color};">需求:</strong> {demand_text} 箱</p>
                            <p><strong style="color: {demand_color};">新需求:</strong> {new_demand_text} 箱</p>
                            <hr>
                            <h4 style="color: #0275d8; margin: 10px 0 5px 0;">任务信息</h4>
                            <p><strong>到达时间:</strong> {stop['arrival_time']}</p>
                            <p><strong>服务开始:</strong> {stop['service_start_time']}</p>
                            <p><strong>完成时间:</strong> {stop['finish_time']}</p>
                            <p><strong>服务后负载:</strong> {stop['load_after_service']}</p>
                        </div>
                        """,
                        max_width=300,
                    ),
                    icon=icon,
                ).add_to(assigned_route_group)

                stop_counter += 1

    # 添加动态线路 AntPath
    if len(route_coordinates) > 1:
        AntPath(
            locations=route_coordinates,
            delay=800,
            dash_array=[10, 20],
            color="#007bff",
            pulse_color="#FFFFFF",
            weight=5,
            opacity=0.8,
            popup="动态行驶路线",
        ).add_to(assigned_route_group)

    # 绘制未指派站点（按原因分组）
    for unassigned in response_data["data"]["unassigned_tasks"]:
        location_id = unassigned["location_id"]
        if location_id in station_id_map:
            station = station_id_map[location_id]
            st_wgs = bd09_to_wgs84(station["longitude"], station["latitude"])

            demand_text = (
                f"+{station['demands']}"
                if station["demands"] >= 0
                else str(station["demands"])
            )
            
            # 确定原因和对应的颜色
            reason = unassigned.get('reason', 'other')
            if reason not in reason_colors:
                reason = 'other'
            color = reason_colors[reason]

            folium.CircleMarker(
                st_wgs,
                radius=6,
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial, sans-serif; max-width: 300px;">
                        <h3 style="color: {color}; margin: 0 0 10px 0;">未指派站点</h3>
                        <p><strong>名称:</strong> {station['station_name']}</p>
                        <p><strong>ID:</strong> {station['station_id']}</p>
                        <p><strong style="color: {color};">需求:</strong> {demand_text} 箱</p>
                        <hr>
                        <h4 style="color: {color}; margin: 10px 0 5px 0;">未指派原因</h4>
                        <p>{unassigned['reason']}</p>
                    </div>
                    """,
                    max_width=300,
                ),
                color=color,
                fill=True,
                fill_opacity=0.7,
            ).add_to(unassigned_groups[reason])

    # 添加图层控制器
    folium.LayerControl().add_to(m)

    # 保存地图
    m.save(output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="物流可视化工具")
    parser.add_argument(
        "--data_file",
        nargs="?",
        default="data/req.json",
        help="输入数据文件路径 (默认: data/req.json)",
    )

    args = parser.parse_args()

    input_map_file = f"input_map.html"
    output_map_file = f"output_map.html"

    # 自动生成响应文件名（基于输入文件名）
    response_file = "data/response.json"

    print(f"输入文件: {args.data_file}")
    print(f"响应文件: {response_file}")
    print(f"站点地图: {input_map_file}")
    print(f"路线地图: {output_map_file}")

    create_visualization(data_file=args.data_file, output_file=input_map_file)
    create_output_visualization(
        req_file=args.data_file,
        response_file=response_file,
        output_file=output_map_file,
    )
