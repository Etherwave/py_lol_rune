import tkinter as tk
from tkinter import ttk
from collections import deque
import os
import json
from lcu import LCU
from PIL import Image, ImageTk
import pystray
import threading

# 符文数据（5个系，每系4行）
RUNES = {
    "精密": [
        ["强攻", "致命节奏", "迅捷步法", "征服者"],
        ["吸收生命力", "凯旋", "气定神闲", ],
        ["传说：欢欣", "传说：急速", "传说：血统"],
        ["致命一击", "砍倒", "坚毅不倒"]
    ],
    "主宰": [
        ["电刑", "黑暗收割", "丛刃"],
        ["恶意中伤", "血之滋味", "猛然冲击"],
        ["第六感", "可怖纪念品", "深入守卫"],
        ["寻宝猎人", "无情猎手", "终极猎人"]
    ],
    "巫术": [
        ["召唤：艾黎", "奥术彗星", "相位猛冲"],
        ["公理秘术", "法力流系带", "灵光披风"],
        ["超然", "迅捷", "绝对专注"],
        ["焦灼", "水上行走", "风暴聚集"]
    ],
    "坚决": [
        ["不灭之握", "余震", "守护者"],
        ["爆破", "生命源泉", "护盾猛击"],
        ["调节", "复苏之风", "骸骨镀层"],
        ["过度生长", "复苏", "坚定"]
    ],
    "启迪": [
        ["冰川增幅", "启封的秘籍", "先攻"],
        ["海克斯科技闪现罗网", "神奇之鞋", "返现"],
        ["三重补药", "时间扭曲补药", "饼干配送"],
        ["星界洞悉", "行进速率", "多面手"]
    ]
}

EXTERN_RUNES = [
    ["+9 适应之力", "+10% 攻击速度", "+8 技能急速"],
    ["+9 适应之力", "+2.5% 移动速度", "+10-180 成长生命值"],
    ["+65 生命值", "+15% 韧性和减速抗性", "+10-180 成长生命值"]
]

RUNE_TEMPLATE = {
    "autoModifiedSelections": [],
    "current": False,
    "id": 1,
    "isActive": False,
    "isDeletable": True,
    "isEditable": True,
    "isRecommendationOverride": False,
    "isTemporary": False,
    "isValid": True,
    "lastModified": 1764846936131,
    "name": "01",
    "order": 1,
    "primaryStyleId": 8000,
    "selectedPerkIds": [
        8008,
        9101,
        9104,
        8014,
        8275,
        8210,
        5008,
        5008,
        5011
    ],
    "subStyleId": 8200
}

class LolRunesGui:
    def __init__(self):
        self.perks_json_file_path = "./perks.json"
        self.perk_styles_json_file_path = "./perk_styles.json"
        self.perks_name_id_map = {}
        self.perk_styles_name_id_map = {}
        self.get_perks_name_id_map()
        self.get_perk_styles_name_id_map()
        self.runes_folder = "./runes/"
        if not os.path.exists(self.runes_folder):
            os.makedirs(self.runes_folder)
        self.icon_path = "./images/icon.png"
        self.image = Image.open(self.icon_path)
        self.lcu = LCU()
        self.setupGuiAndTray()

    def setupGuiAndTray(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("英雄联盟符文配置器")
        self.width = 500
        self.line_dis = 30
        self.hight = 170 + 15 * self.line_dis
        self.root.geometry(f"{self.width}x{self.hight}")
        self.root.iconphoto(False, ImageTk.PhotoImage(self.image))
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.primary_choice = tk.StringVar(value="精密")
        self.secondary_choice = tk.StringVar(value="主宰")

        self.primary_vars = [tk.StringVar() for _ in range(4)]
        self.secondary_vars = [tk.StringVar() for _ in range(3)]
        self.extern_vars = [tk.StringVar() for _ in range(3)]
        self.secondary_active_rows = deque(maxlen=2)

        self.create_widgets()
        self.update_all()

        self.icon = pystray.Icon("launcher", self.image, "lol符文应用")
        self.update_menu()

    def get_perks_name_id_map(self):
        self.perks_name_id_map = {}
        perks_json = None
        if os.path.exists(self.perks_json_file_path):
            with open(self.perks_json_file_path, "r", encoding='utf-8') as f:
                perks_json = json.load(f)
        if perks_json is None:
            perks_json = self.lcu.get_perks()
            with open(self.perks_json_file_path, 'w', encoding='utf-8') as f:
                json.dump(perks_json, f, ensure_ascii=False, indent=4)
        if perks_json is None:
            return
        for item in perks_json:
            self.perks_name_id_map[item['name']] = item['id']

    def get_perk_styles_name_id_map(self):
        self.perk_styles_name_id_map = {}
        perks_styles_json = None
        if os.path.exists(self.perk_styles_json_file_path):
            with open(self.perk_styles_json_file_path, "r", encoding='utf-8') as f:
                perks_styles_json = json.load(f)
        if perks_styles_json is None:
            perks_styles_json = self.lcu.get_perk_styles()
            with open(self.perk_styles_json_file_path, 'w', encoding='utf-8') as f:
                json.dump(perks_styles_json, f, ensure_ascii=False, indent=4)
        if perks_styles_json is None:
            return
        for item in perks_styles_json:
            self.perk_styles_name_id_map[item['name']] = item['id']

    def create_widgets(self):
        # 主系选择
        primary_frame = ttk.Frame(self.root)
        primary_frame.pack(fill="x", padx=10, pady=5)
        primary_label_frame = ttk.LabelFrame(primary_frame, text="主系天赋", padding=10)
        primary_label_frame.pack(fill="x", padx=10, pady=5)
        for i, name in enumerate(RUNES):
            ttk.Radiobutton(
                primary_label_frame, text=name,
                variable=self.primary_choice, value=name,
                command=self.on_primary_change
            ).grid(row=0, column=i, padx=5)

        self.primary_detail = ttk.Frame(primary_frame, padding=(10, 0))
        self.primary_detail.pack(fill="x", padx=10, pady=5)

        # 副系选择
        secondary_frame = ttk.Frame(self.root)
        secondary_frame.pack(fill="x", padx=10, pady=5)
        secondary_label_frame = ttk.LabelFrame(secondary_frame, text="副系天赋", padding=10)
        secondary_label_frame.pack(fill="x", padx=10, pady=5)
        for i, name in enumerate(RUNES):
            ttk.Radiobutton(
                secondary_label_frame, text=name,
                variable=self.secondary_choice, value=name,
                command=self.on_secondary_change
            ).grid(row=0, column=i, padx=5)

        self.secondary_detail = ttk.Frame(secondary_frame, padding=(10, 0))
        self.secondary_detail.pack(fill="x", padx=10, pady=5)

        self.extren_rune_frame = ttk.Frame(self.root, padding=(10, 0))
        self.extren_rune_frame.pack(fill="x", padx=10, pady=5)

        self.extren_rune_label_frame = ttk.LabelFrame(self.extren_rune_frame, text="外部符文", padding=10)
        self.extren_rune_label_frame.pack(fill="x", padx=10, pady=5)
        for i, rune in enumerate(EXTERN_RUNES):
            for j, perk in enumerate(rune):
                ttk.Radiobutton(
                    self.extren_rune_label_frame, text=perk,
                    variable=self.extern_vars[i], value=perk,
                ).grid(row=i, column=j, padx=5)
            self.extern_vars[i].set(rune[0])
        self.extren_rune_detail = ttk.Frame(self.extren_rune_frame, padding=(10, 0))
        self.extren_rune_detail.pack(fill="x", padx=10, pady=5)

        self.save_rune_frame = ttk.Frame(self.root, padding=(10, 0))
        self.button_save_rune = ttk.Button(self.save_rune_frame, text="保存符文", command=self.save_rune)
        self.button_save_rune.pack(side="right", padx=10, pady=5)
        self.save_rune_frame.pack(fill="x", padx=10, pady=5)

    def auto_gen_new_rune_file_name(self):
        rune_file_name = f"{self.primary_choice.get()}_{self.secondary_choice.get()}"
        for i in range(4):
            rune_file_name += f"_{self.primary_vars[i].get()}"
        for i in range(2):
            rune_file_name += f"_{self.secondary_vars[self.secondary_active_rows[i]].get()}"
        for i in range(3):
            rune_file_name += f"_{self.extern_vars[i].get().split()[-1]}"
        rune_file_name = rune_file_name.replace(" ", "_")
        rune_file_name = rune_file_name.replace(":", "_")
        rune_file_name = rune_file_name.replace("：", "_")
        return rune_file_name + ".json"

    def save_rune(self):
        rune_file_path = os.path.join(self.runes_folder, self.auto_gen_new_rune_file_name())
        rune_name = os.path.basename(rune_file_path)[:-5]
        rune = RUNE_TEMPLATE.copy()
        rune["name"] = rune_name
        rune["selectedPerkIds"] = []
        rune["primaryStyleId"] = self.perk_styles_name_id_map[self.primary_choice.get()]
        rune["subStyleId"] = self.perk_styles_name_id_map[self.secondary_choice.get()]
        for i in range(len(self.primary_vars)):
            rune["selectedPerkIds"].append(self.perks_name_id_map[self.primary_vars[i].get()])
        for i in range(len(self.secondary_active_rows)):
            rune["selectedPerkIds"].append(self.perks_name_id_map[self.secondary_vars[self.secondary_active_rows[i]].get()])
        for i in range(len(self.extern_vars)):
            rune["selectedPerkIds"].append(self.perks_name_id_map[self.extern_vars[i].get().split()[-1]])
        with open(rune_file_path, mode='w', encoding='utf-8') as f:
            f.write(json.dumps(rune, ensure_ascii=False, indent=4))
        self.button_save_rune.config(text="保存成功")
        self.root.after(1000, lambda: self.button_save_rune.config(text="保存符文"))
        if self.icon:
            self.update_menu()

    def clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def on_primary_change(self):
        if self.primary_choice.get() == self.secondary_choice.get():
            for key in RUNES:
                if key != self.primary_choice.get():
                    self.secondary_choice.set(key)
                    break
        self.update_all()

    def on_secondary_change(self):
        if self.primary_choice.get() == self.secondary_choice.get():
            for key in RUNES:
                if key != self.secondary_choice.get():
                    self.primary_choice.set(key)
                    break
        self.update_all()

    def update_all(self):
        self.update_primary()
        self.update_secondary()

    def update_primary(self):
        self.clear_frame(self.primary_detail)
        rows = RUNES[self.primary_choice.get()]
        for i, options in enumerate(rows):
            for j, opt in enumerate(options):
                ttk.Radiobutton(
                    self.primary_detail, text=opt,
                    variable=self.primary_vars[i], value=opt
                ).grid(row=i, column=j, padx=8, pady=2, sticky="w")
            self.primary_vars[i].set(options[0])

    def on_secondary_click(self, row_idx, rune_name):
        self.secondary_vars[row_idx].set(rune_name)
        if row_idx in self.secondary_active_rows:
            self.secondary_active_rows.remove(row_idx)
        self.secondary_active_rows.append(row_idx)
        # 清除未激活行
        for idx in range(3):
            if idx not in self.secondary_active_rows:
                self.secondary_vars[idx].set("")

    def update_secondary(self):
        self.clear_frame(self.secondary_detail)
        rows = RUNES[self.secondary_choice.get()][1:4]  # 取 row1~3
        self.secondary_active_rows.clear()
        # 默认激活前两行
        self.secondary_active_rows.extend([0, 1])

        for i, options in enumerate(rows):
            for j, opt in enumerate(options):
                ttk.Radiobutton(
                    self.secondary_detail, text=opt,
                    variable=self.secondary_vars[i],
                    value=opt,
                    command=lambda r=i, o=opt: self.on_secondary_click(r, o)
                ).grid(row=i, column=j, padx=8, pady=2, sticky="w")
            if i < 2:
                self.secondary_vars[i].set(options[0])
            else:
                self.secondary_vars[i].set("")

    def show_window(self):
        self.root.deiconify()
        self.root.lift()  # 提升到顶层
        self.root.focus_force()  # 强制获取焦点（可选）

    def hide_window(self):
        self.root.withdraw()

    def exit_app(self):
        if self.icon:
            self.icon.stop()
        if self.root:
            self.root.destroy()

    def update_menu(self):
        self.menuItems = []
        self.runes = [f[:-5] for f in os.listdir(self.runes_folder) if f.endswith(".json")]

        # 创建一个处理所有符文点击的通用函数
        def on_rune_clicked(icon, item):
            # item.text 就是符文名称
            rune_name = item.text
            return self.apply_rune(rune_name)

        for rune in self.runes:
            self.menuItems.append(pystray.MenuItem(rune, on_rune_clicked))
        self.menuItems.append(pystray.Menu.SEPARATOR)
        self.menuItems.append(pystray.MenuItem("制作符文", lambda: self.show_window()))
        self.menuItems.append(pystray.MenuItem("退出", lambda: self.exit_app()))
        self.menu = pystray.Menu(*self.menuItems)
        self.icon.menu = self.menu
        self.icon.update_menu()

    def apply_rune(self, rune_file_name):
        rune_file_path = self.runes_folder + rune_file_name + '.json'
        self.lcu.apply_rune(rune_file_path)

    def run(self):
        # 托盘在后台线程运行
        icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        icon_thread.start()
        self.root.mainloop()

if __name__ == "__main__":
    app = LolRunesGui()
    app.run()