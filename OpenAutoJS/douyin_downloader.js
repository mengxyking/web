"ui";

importClass(java.net.URL);
importClass(java.net.HttpURLConnection);
importClass(java.io.FileOutputStream);
importClass(java.io.File);
importClass(android.os.Environment);
importClass(javax.net.ssl.SSLContext);
importClass(javax.net.ssl.HttpsURLConnection);
importClass(javax.net.ssl.X509TrustManager);
importClass(android.widget.TextView);
importClass(android.widget.LinearLayout);
importClass(android.graphics.Color);
importClass(android.view.Gravity);
importClass(android.view.View);
importClass(android.text.InputType);
importClass(android.util.TypedValue);

// ─── SSL ─────────────────────────────────────────────────────────────────────
(function () {
    var ta = [new JavaAdapter(X509TrustManager, {
        checkClientTrusted: function () {},
        checkServerTrusted: function () {},
        getAcceptedIssuers: function () { return []; }
    })];
    var sc = SSLContext.getInstance("SSL");
    sc.init(null, ta, new java.security.SecureRandom());
    HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
    HttpsURLConnection.setDefaultHostnameVerifier(function () { return true; });
})();

// ─── 常量 ────────────────────────────────────────────────────────────────────
var MOBILE_UA  = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148";
var ANDROID_UA = "com.ss.android.ugc.aweme/110101 (Linux; U; Android 10; zh_CN; Pixel 4; Build/QQ3A.200805.001; Cronet/58.0.2991.0)";
var PC_UA      = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";
var DOUYIN_PKG = "com.ss.android.ugc.aweme";

// ─── 运行时状态 ───────────────────────────────────────────────────────────────
var savePath       = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath();
var downloading    = false;
var autoRunning    = false;
var autoThread     = null;
var floatWin       = null;
var collectCount   = 0;
var dlQueue        = [];
var dlQueueRunning = false;
var onePixelView   = null;   // 1像素前台保活窗口

// ─── 布局 ────────────────────────────────────────────────────────────────────
ui.layout(
    <vertical bg="#0F0F0F" h="match_parent">

        {/* ── 顶部标题栏 ── */}
        <horizontal id="appTitleBar" w="match_parent" padding="20 36 20 12" bg="#141414" gravity="center_vertical">
            <text id="pageTitle" text="手动下载" textSize="20sp" textStyle="bold" textColor="#FFFFFF" layout_weight="1"/>
            <text text="无水印" textSize="10sp" textColor="#FF4444" bg="#2A0A0A" padding="6 3 6 3"/>
        </horizontal>

        {/* ── 内容区（可滚动）── */}
        <scroll id="mainScroll" w="match_parent" layout_weight="1">
            <vertical w="match_parent">

                {/* ═══════════ 手动下载 ═══════════ */}
                <vertical id="pageManual" w="match_parent">

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 12 16 8" padding="16 14 16 14">
                        <horizontal gravity="center_vertical" marginBottom="10">
                            <text text="分享链接" textSize="13sp" textStyle="bold" textColor="#EEEEEE" layout_weight="1"/>
                            <text id="urlCountLabel" text="" textSize="10sp" textColor="#FF4444"/>
                        </horizontal>
                        <input id="urlInput"
                               hint="粘贴抖音链接或含链接的文字 · 批量每行一个"
                               hintColor="#3A3A3A" textSize="12sp" textColor="#E0E0E0"
                               bg="#141414" w="match_parent" h="120" padding="12 10 12 10"/>
                        <horizontal w="match_parent" marginTop="12">
                            <button id="pasteBtn" text="粘 贴" bg="#2A2A2A" textColor="#DDDDDD"
                                    textSize="12sp" h="40" layout_weight="1"/>
                            <button id="clearBtn" text="清 空" bg="#141414" textColor="#555555"
                                    textSize="12sp" h="40" layout_weight="1" marginLeft="10"/>
                        </horizontal>
                    </vertical>

                    <horizontal bg="#1C1C1C" w="match_parent" margin="16 0 16 8"
                                padding="14 11 10 11" gravity="center_vertical">
                        <text text="📂" textSize="14sp" marginRight="8"/>
                        <text id="pathLabel" textSize="10sp" textColor="#888888"
                              layout_weight="1" singleLine="true" ellipsize="start"/>
                        <button id="chooseBtn" text="浏览" bg="#FF4444" textColor="white"
                                textSize="11sp" h="34" w="60" marginLeft="10"/>
                    </horizontal>

                    <button id="dlBtn" text="开  始  下  载" textSize="15sp" textStyle="bold"
                            textColor="white" bg="#FF4444" w="match_parent" margin="16 0 16 8" h="54"/>

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 0 16 8" padding="14 12 14 10">
                        <horizontal w="match_parent" gravity="center_vertical">
                            <text id="statusLabel" text="准备就绪" textSize="10sp" textColor="#666666" layout_weight="1"/>
                            <text id="batchLabel" text="" textSize="10sp" textColor="#FF4444"/>
                        </horizontal>
                        <progressbar id="progressBar" w="match_parent" h="4" marginTop="10"
                                     style="?android:attr/progressBarStyleHorizontal" max="100" progress="0"/>
                    </vertical>

                </vertical>

                {/* ═══════════ App 采集 ═══════════ */}
                <vertical id="pageApp" w="match_parent">

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 12 16 8" padding="16 14 16 6">
                        <text text="权限配置" textSize="12sp" textStyle="bold" textColor="#EEEEEE" marginBottom="12"/>

                        <horizontal id="accRow" w="match_parent" bg="#252525"
                                    padding="14 12 10 12" gravity="center_vertical" marginBottom="6">
                            <vertical layout_weight="1">
                                <text text="无障碍服务" textSize="12sp" textStyle="bold" textColor="#EEEEEE"/>
                                <text text="模拟点击分享按钮、滑动视频" textSize="10sp" textColor="#555555" marginTop="2"/>
                            </vertical>
                            <text id="accToggle" text="未开启" textSize="11sp"
                                  textColor="#FF5252" padding="10 5 10 5"/>
                        </horizontal>

                        <horizontal id="floatRow" w="match_parent" bg="#252525"
                                    padding="14 12 10 12" gravity="center_vertical" marginBottom="4">
                            <vertical layout_weight="1">
                                <text text="悬浮窗权限" textSize="12sp" textStyle="bold" textColor="#EEEEEE"/>
                                <text text="采集时在抖音上方显示停止按钮" textSize="10sp" textColor="#555555" marginTop="2"/>
                            </vertical>
                            <text id="floatToggle" text="未开启" textSize="11sp"
                                  textColor="#FF5252" padding="10 5 10 5"/>
                        </horizontal>

                        <text text="· 点击未开启的权限行可跳转到对应设置页面" textSize="9sp"
                              textColor="#444444" marginTop="6" marginBottom="4"/>
                    </vertical>

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 0 16 20" padding="16 14 16 14">
                        <horizontal gravity="center_vertical" marginBottom="14">
                            <text id="autoStatusDot" text="●" textSize="16sp" textColor="#333333"/>
                            <text id="autoStatusLabel" text="  采集未运行" textSize="12sp"
                                  textStyle="bold" textColor="#888888" layout_weight="1" marginLeft="4"/>
                            <text id="collectLabel" text="0" textSize="13sp" textStyle="bold" textColor="#FF8C00"/>
                            <text text=" 个已采集" textSize="10sp" textColor="#555555"/>
                        </horizontal>

                        <text id="autoDetailLabel" text="就绪" textSize="10sp"
                              textColor="#555555" marginBottom="14"/>

                        <horizontal w="match_parent">
                            <button id="autoStartBtn" text="开始采集" bg="#FF8C00" textColor="white"
                                    textSize="13sp" textStyle="bold" h="50" layout_weight="1"/>
                            <button id="autoStopBtn" text="停止" bg="#2A2A2A" textColor="#777777"
                                    textSize="13sp" h="50" w="90" marginLeft="10"/>
                        </horizontal>
                    </vertical>

                </vertical>

                {/* ═══════════ API 采集 ═══════════ */}
                <vertical id="pageApi" w="match_parent">

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 12 16 8" padding="16 14 16 14">

                        <horizontal gravity="center_vertical" marginBottom="12">
                            <text text="API 采集" textSize="12sp" textStyle="bold" textColor="#EEEEEE" layout_weight="1"/>
                            <text text="无需打开抖音App" textSize="9sp" textColor="#444444" marginRight="8"/>
                            <text id="apiLoginStatus" text="未登录" textSize="10sp" textColor="#FF5252"/>
                        </horizontal>

                        <button id="apiLoginBtn" text="登录抖音账号（网页版）"
                                bg="#252525" textColor="#DDDDDD" textSize="12sp" h="42"
                                w="match_parent" marginBottom="10"/>

                        <horizontal w="match_parent" gravity="center_vertical" marginBottom="6">
                            <text text="频道" textSize="11sp" textColor="#888888" marginRight="6"/>
                            <spinner id="apiFeedTab"
                                     entries="推荐|精选|关注|朋友"
                                     bg="#252525" textColor="#EEEEEE" textSize="11sp"
                                     h="36" w="90"/>
                            <text text="数量" textSize="11sp" textColor="#888888" marginLeft="8" marginRight="6"/>
                            <input id="apiFeedCount" text="20" textSize="12sp" textColor="#EEEEEE"
                                   bg="#252525" w="52" h="36" padding="8 4" inputType="number"/>
                        </horizontal>

                        <button id="apiFeedBtn" text="开始采集" bg="#FF8C00" textColor="white"
                                textSize="12sp" h="42" w="match_parent" textStyle="bold" marginBottom="8"/>

                        <horizontal w="match_parent" gravity="center_vertical">
                            <input id="apiUserUrl" hint="用户主页链接 (douyin.com/user/...)"
                                   hintColor="#333333" textSize="11sp" textColor="#E0E0E0"
                                   bg="#252525" layout_weight="1" h="36" padding="10 4"/>
                            <button id="apiUserBtn" text="拉取" bg="#FF8C00" textColor="white"
                                    textSize="11sp" h="36" w="60" marginLeft="8"/>
                        </horizontal>

                    </vertical>

                </vertical>

                {/* ═══════════ 设置 ═══════════ */}
                <vertical id="pageSettings" w="match_parent">

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 12 16 8" padding="16 14 16 14">
                        <text text="下载路径" textSize="12sp" textStyle="bold" textColor="#EEEEEE" marginBottom="10"/>
                        <text id="pathLabelSettings" textSize="10sp" textColor="#888888"
                              w="match_parent" padding="12 10 12 10" bg="#252525" marginBottom="10"/>
                        <button id="chooseBtnSettings" text="更改路径" bg="#FF4444" textColor="white"
                                textSize="12sp" h="40" w="match_parent"/>
                    </vertical>

                    <vertical bg="#1C1C1C" w="match_parent" margin="16 0 16 20" padding="16 14 16 14">
                        <text text="关于" textSize="12sp" textStyle="bold" textColor="#EEEEEE" marginBottom="10"/>
                        <text text="抖音无水印下载器" textSize="11sp" textColor="#888888"/>
                        <text text="基于 AutoX.js  ·  仅供学习研究使用" textSize="10sp" textColor="#444444" marginTop="4"/>
                    </vertical>

                </vertical>

                {/* ═══════════ 共用日志区 ═══════════ */}
                <vertical id="logSection" w="match_parent">

                    <horizontal w="match_parent" padding="16 10 16 4" gravity="center_vertical">
                        <text text="采集日志" textSize="11sp" textStyle="bold" textColor="#DDDDDD" layout_weight="1"/>
                        <text id="clearCollectLogBtn" text="清空" textSize="10sp" textColor="#444444" padding="8 4 4 4"/>
                    </horizontal>
                    <text id="collectLogTv" text="" textSize="10sp" textColor="#999999"
                          w="match_parent" margin="16 0 16 4" padding="10" bg="#0A0A0A"/>

                    <horizontal w="match_parent" padding="16 6 16 4" gravity="center_vertical">
                        <text text="下载日志" textSize="11sp" textStyle="bold" textColor="#DDDDDD" layout_weight="1"/>
                        <text id="clearDownloadLogBtn" text="清空" textSize="10sp" textColor="#444444" padding="8 4 4 4"/>
                    </horizontal>
                    <text id="downloadLogTv" text="" textSize="10sp" textColor="#999999"
                          w="match_parent" margin="16 0 16 4" padding="10" bg="#0A0A0A"/>

                    <horizontal w="match_parent" padding="16 6 16 4" gravity="center_vertical">
                        <text text="下载记录" textSize="11sp" textStyle="bold" textColor="#DDDDDD" layout_weight="1"/>
                        <text id="clearHistoryBtn" text="清空" textSize="10sp" textColor="#444444" padding="6 4 2 4"/>
                    </horizontal>
                    <vertical id="historyContainer" w="match_parent" margin="16 0 16 20" bg="#1C1C1C" padding="0"/>

                </vertical>

            </vertical>
        </scroll>

        {/* ── 播放器（在 ScrollView 外，独占内容区高度）── */}
        <vertical id="pagePlayer" w="match_parent" h="0"/>

        {/* ── 底部 Tab 栏 ── */}
        <horizontal id="appTabDivider" w="match_parent" h="2" bg="#222222"/>
        <horizontal id="appTabBar" w="match_parent" h="60" bg="#141414">

            <vertical id="tabManual" layout_weight="1" gravity="center" padding="6 4 6 4">
                <text id="tabManualIcon" text="⬇" textSize="22sp" textColor="#FF4444"
                      gravity="center" w="match_parent"/>
                <text id="tabManualLabel" text="手动下载" textSize="9sp" textColor="#FF4444"
                      gravity="center" w="match_parent"/>
            </vertical>

            <vertical id="tabApp" layout_weight="1" gravity="center" padding="6 4 6 4">
                <text id="tabAppIcon" text="◉" textSize="20sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
                <text id="tabAppLabel" text="App采集" textSize="9sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
            </vertical>

            <vertical id="tabApi" layout_weight="1" gravity="center" padding="6 4 6 4">
                <text id="tabApiIcon" text="⊙" textSize="20sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
                <text id="tabApiLabel" text="API采集" textSize="9sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
            </vertical>

            <vertical id="tabPlayer" layout_weight="1" gravity="center" padding="6 4 6 4">
                <text id="tabPlayerIcon" text="▶" textSize="20sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
                <text id="tabPlayerLabel" text="播放器" textSize="9sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
            </vertical>

            <vertical id="tabSettings" layout_weight="1" gravity="center" padding="6 4 6 4">
                <text id="tabSettingsIcon" text="⚙" textSize="20sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
                <text id="tabSettingsLabel" text="设置" textSize="9sp" textColor="#555555"
                      gravity="center" w="match_parent"/>
            </vertical>

        </horizontal>

    </vertical>
);

// ─── 初始化 ──────────────────────────────────────────────────────────────────
ui.pathLabel.setText(savePath);
ui.pathLabelSettings.setText(savePath);
ui.urlInput.setSingleLine(false);
ui.urlInput.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
ui.urlInput.setGravity(Gravity.TOP | Gravity.START);
ui.urlInput.setMaxLines(10);

// 默认隐藏非首页的所有页面（pagePlayer 在 scroll 外，初始 h=0 已隐藏）
ui.pageApp.setVisibility(View.GONE);
ui.pageApi.setVisibility(View.GONE);
ui.pageSettings.setVisibility(View.GONE);

// 布局渲染完成后读剪贴板（App 刚启动处于前台，Android 10+ 无限制）
ui.post(function () {
    try {
        var clip = getClip();
        if (clip && clip.trim().length > 0) {
            ui.urlInput.setText(clip.trim());
            toast("已读取剪贴板内容");
        }
    } catch (e) {}
});

// ─── 底部 Tab 导航 ────────────────────────────────────────────────────────────
var C_ACCENT  = Color.parseColor("#FF4444");
var C_ORANGE  = Color.parseColor("#FF8C00");
var C_GREEN   = Color.parseColor("#4CAF50");
var C_BLUE    = Color.parseColor("#2196F3");
var C_SILVER  = Color.parseColor("#9E9E9E");
var C_DARK    = Color.parseColor("#1C1C1C");
var C_WHITE   = Color.WHITE;
var C_GREY    = Color.parseColor("#555555");

var _TAB_DEFS = [
    { key: "manual",   title: "手动下载", color: "#FF4444",
      icon: ui.tabManualIcon,   label: ui.tabManualLabel,   page: ui.pageManual   },
    { key: "app",      title: "App 采集", color: "#FF8C00",
      icon: ui.tabAppIcon,      label: ui.tabAppLabel,      page: ui.pageApp      },
    { key: "api",      title: "API 采集", color: "#4CAF50",
      icon: ui.tabApiIcon,      label: ui.tabApiLabel,      page: ui.pageApi      },
    { key: "player",   title: "播放器",   color: "#2196F3",
      icon: ui.tabPlayerIcon,   label: ui.tabPlayerLabel,   page: ui.pagePlayer   },
    { key: "settings", title: "设置",     color: "#9E9E9E",
      icon: ui.tabSettingsIcon, label: ui.tabSettingsLabel, page: ui.pageSettings }
];

var _currentTab = "manual";

function showPage(tab) {
    _currentTab = tab;
    var isPlayer = (tab === "player");
    var MATCH = android.widget.LinearLayout.LayoutParams.MATCH_PARENT;

    // 播放器页：在 scroll 外独占内容区高度；其余页：在 scroll 内切换
    ui.mainScroll.setLayoutParams(new android.widget.LinearLayout.LayoutParams(MATCH, 0, isPlayer ? 0 : 1));
    ui.mainScroll.setVisibility(isPlayer ? View.GONE : View.VISIBLE);
    ui.pagePlayer.setLayoutParams(new android.widget.LinearLayout.LayoutParams(MATCH, 0, isPlayer ? 1 : 0));
    ui.pagePlayer.setVisibility(isPlayer ? View.VISIBLE : View.GONE);
    // 播放器模式：隐藏顶部标题栏，扩大播放区域
    ui.appTitleBar.setVisibility(isPlayer ? View.GONE : View.VISIBLE);

    // 非播放器页内：显示/隐藏对应 page
    var scrollKeys = ["manual", "app", "api", "settings"];
    for (var i = 0; i < _TAB_DEFS.length; i++) {
        var d = _TAB_DEFS[i];
        if (scrollKeys.indexOf(d.key) >= 0) {
            d.page.setVisibility((!isPlayer && d.key === tab) ? View.VISIBLE : View.GONE);
        }
        // Tab 图标颜色
        var isActive = (d.key === tab);
        var col = Color.parseColor(isActive ? d.color : "#555555");
        d.icon.setTextColor(col);
        d.label.setTextColor(col);
        if (isActive) ui.pageTitle.setText(d.title);
    }

    // 日志区：手动/App/API 显示
    ui.logSection.setVisibility((!isPlayer && (tab === "manual" || tab === "app" || tab === "api")) ? View.VISIBLE : View.GONE);

    if (tab === "app") refreshPermUI();

    if (isPlayer) {
        if (!_pInited) initPlayer();
    } else {
        if (_vv && _vv.isPlaying()) _vv.pause();
    }
}

ui.tabManual.on("click",   function () { showPage("manual");   });
ui.tabApp.on("click",      function () { showPage("app");      });
ui.tabApi.on("click",      function () { showPage("api");      });
ui.tabPlayer.on("click",   function () { showPage("player");   });
ui.tabSettings.on("click", function () { showPage("settings"); });

// ─── 权限检测与 UI 刷新 ───────────────────────────────────────────────────────
function hasAccessibility() {
    try {
        // 1. 系统无障碍总开关
        var globalOn = android.provider.Settings.Secure.getInt(
            activity.getContentResolver(),
            android.provider.Settings.Secure.ACCESSIBILITY_ENABLED, 0
        ) === 1;
        if (!globalOn) return false;
        // 2. 当前 App 的无障碍服务在已启用列表中
        var enabled = android.provider.Settings.Secure.getString(
            activity.getContentResolver(),
            android.provider.Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) || "";
        return enabled.toLowerCase().indexOf(activity.getPackageName().toLowerCase()) !== -1;
    } catch (e) {
        return auto.service != null;
    }
}

function hasFloatWindow() {
    try {
        if (android.os.Build.VERSION.SDK_INT >= 23) {
            return android.provider.Settings.canDrawOverlays(activity);
        }
        return true;
    } catch (e) { return false; }
}

function refreshPermUI() {
    var acc   = hasAccessibility();
    var float = hasFloatWindow();

    ui.run(function () {
        // 无障碍
        ui.accToggle.setText(acc ? "已开启  ✓" : "未开启  →");
        ui.accToggle.setTextColor(Color.parseColor(acc ? "#4CAF50" : "#FF5252"));

        // 悬浮窗
        ui.floatToggle.setText(float ? "已开启  ✓" : "未开启  →");
        ui.floatToggle.setTextColor(Color.parseColor(float ? "#4CAF50" : "#FF5252"));
    });
}

// 点击权限行 → 若未开启则跳转设置
ui.accRow.on("click", function () {
    if (!hasAccessibility()) {
        toast("请在无障碍设置中找到 AutoJS 并开启");
        app.startActivity({ action: "android.settings.ACCESSIBILITY_SETTINGS" });
    } else {
        toast("无障碍服务已开启 ✓");
    }
});

ui.floatRow.on("click", function () {
    if (!hasFloatWindow()) {
        try {
            var intent = new android.content.Intent(
                android.provider.Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                android.net.Uri.parse("package:" + activity.getPackageName())
            );
            activity.startActivity(intent);
        } catch (e) {
            app.startActivity({ action: "android.settings.ACTION_MANAGE_OVERLAY_PERMISSION" });
        }
    } else {
        toast("悬浮窗权限已开启 ✓");
    }
});

// ─── 手动下载事件 ─────────────────────────────────────────────────────────────
ui.pasteBtn.on("click", function () {
    var t = getClip(); if (t) ui.urlInput.setText(t.trim());
});
ui.clearBtn.on("click", function () {
    ui.urlInput.setText(""); ui.urlCountLabel.setText("");
});
ui.clearHistoryBtn.on("click", function () {
    ui.historyContainer.removeAllViews();
});
ui.urlInput.addTextChangedListener(new JavaAdapter(android.text.TextWatcher, {
    afterTextChanged: function (s) {
        var n = extractAllUrls(s.toString()).length;
        ui.urlCountLabel.setText(n > 1 ? n + " 个链接" : "");
    },
    beforeTextChanged: function () {}, onTextChanged: function () {}
}));
ui.chooseBtn.on("click", function () {
    threads.start(function () { browseFolder(savePath); });
});
ui.chooseBtnSettings.on("click", function () {
    threads.start(function () { browseFolder(savePath); });
});
ui.dlBtn.on("click", function () {
    if (downloading) return;
    var t = ui.urlInput.getText().toString().trim();
    if (!t) { toast("请先粘贴抖音分享链接"); return; }
    startManualDownload(t);
});

// ─── 自动采集事件 ─────────────────────────────────────────────────────────────
ui.autoStartBtn.on("click", function () {
    if (autoRunning) { toast("采集已在运行"); return; }
    // UI 线程立刻返回，所有阻塞逻辑在子线程执行
    autoThread = threads.start(function () { beginAutoCollect(); });
});
ui.autoStopBtn.on("click", function () {
    stopAutoCollect();
});

// ─── 文件夹浏览（子线程阻塞调用） ────────────────────────────────────────────
function browseFolder(startPath) {
    var dir = new File(startPath);
    if (!dir.exists() || !dir.isDirectory())
        dir = new File(Environment.getExternalStorageDirectory().getAbsolutePath());

    var labels = ["✔ 选择此目录"], paths = ["__use__"];
    var parent = dir.getParentFile();
    if (parent && parent.canRead()) {
        labels.push("↑ 返回上级：" + parent.getName());
        paths.push("__up__");
    }
    var files = dir.listFiles() || [], subdirs = [];
    for (var i = 0; i < files.length; i++)
        if (files[i].isDirectory() && !files[i].getName().startsWith(".")) subdirs.push(files[i]);
    subdirs.sort(function (a, b) { return String(a.getName()).localeCompare(String(b.getName())); });
    for (var i = 0; i < subdirs.length; i++) {
        labels.push("📁  " + subdirs[i].getName()); paths.push(subdirs[i].getAbsolutePath());
    }

    var idx = dialogs.select(dir.getAbsolutePath(), labels);
    if (idx < 0) return;
    if (paths[idx] === "__use__") {
        savePath = dir.getAbsolutePath();
        ui.run(function () {
            ui.pathLabel.setText(savePath);
            ui.pathLabelSettings.setText(savePath);
        });
    } else if (paths[idx] === "__up__") {
        browseFolder(parent.getAbsolutePath());
    } else {
        browseFolder(paths[idx]);
    }
}

// ─── UI 辅助 ─────────────────────────────────────────────────────────────────
function setStatus(t)   { ui.run(function () { ui.statusLabel.setText(t); }); }
function setProgress(p) { ui.run(function () { ui.progressBar.setProgress(Math.round(p)); }); }
function setBatch(t)    { ui.run(function () { ui.batchLabel.setText(t); }); }
function setAutoDetail(t) { ui.run(function () { ui.autoDetailLabel.setText(t); }); }

function addLog(msg) {
    console.log(msg);
}

// ─── 日志 TextView 状态 ───────────────────────────────────────────────────────
var _collectLines  = [];
var _downloadLines = [];

function addCollectLog(msg) {
    console.log("[采集] " + msg);
    _collectLines.push(msg);
    if (_collectLines.length > 80) _collectLines.shift();
    ui.run(function () {
        try { ui.collectLogTv.setText(_collectLines.join("\n")); } catch (e) {}
    });
    updateCollectOverlay(msg);
}

function addDownloadLog(msg) {
    console.log("[下载] " + msg);
    _downloadLines.push(msg);
    if (_downloadLines.length > 80) _downloadLines.shift();
    ui.run(function () {
        try { ui.downloadLogTv.setText(_downloadLines.join("\n")); } catch (e) {}
    });
}

function dpToPx(dp) {
    var density = activity.getResources().getDisplayMetrics().density;
    return Math.round(dp * density);
}

// ─── 后台剪贴板监听（Android 12+ 唯一可靠方案）────────────────────────────────
// 系统主动推送 onPrimaryClipChanged 时读剪贴板，此时不受后台限制
var lastClipText = "";
var _clipCm      = null;

function setupClipboardMonitor() {
    try {
        if (!auto.service) { addLog("⚠ 无障碍服务未就绪，剪贴板监听跳过"); return; }
        if (_clipCm) return;   // 已注册
        _clipCm = auto.service.getSystemService(android.content.Context.CLIPBOARD_SERVICE);
        _clipCm.addPrimaryClipChangedListener(
            new JavaAdapter(android.content.ClipboardManager.OnPrimaryClipChangedListener, {
                onPrimaryClipChanged: function () {
                    try {
                        var data = _clipCm.getPrimaryClip();
                        if (data && data.getItemCount() > 0) {
                            var t = String(data.getItemAt(0).coerceToText(auto.service));
                            if (t && t.length > 0) {
                                lastClipText = t;
                                addLog("📋 剪贴板更新: " + t.substring(0, 60));
                            }
                        }
                    } catch (e) { addLog("剪贴板回调读取失败: " + e.message); }
                }
            })
        );
        addLog("● 剪贴板监听已注册");
    } catch (e) { addLog("剪贴板监听注册失败: " + e.message); }
}

function getClipSafe() {
    // 优先返回监听器捕获的值；前台时降级用内置 getClip()
    if (lastClipText) return lastClipText;
    try { return getClip() || ""; } catch (e) { return ""; }
}

function addHistory(text, ok) {
    ui.run(function () {
        var tv  = new TextView(activity);
        tv.setText(text);
        tv.setTextColor(Color.parseColor(ok ? "#4CAF50" : "#FF5252"));
        tv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10.5);
        tv.setPadding(14, 10, 14, 10);
        tv.setLayoutParams(new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        ui.historyContainer.addView(tv, 0);
        var div = new View(activity);
        var dlp = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1);
        div.setLayoutParams(dlp); div.setBackgroundColor(Color.parseColor("#2A2A2A"));
        ui.historyContainer.addView(div, 1);
    });
}

// ─── 手动/批量下载 ────────────────────────────────────────────────────────────
function startManualDownload(inputText) {
    var urls = extractAllUrls(inputText);
    if (!urls.length) { dialogs.alert("提示", "未找到有效的抖音链接"); return; }
    downloading = true;
    ui.run(function () { ui.dlBtn.setText("下载中..."); ui.dlBtn.setEnabled(false); });
    setProgress(0);

    threads.start(function () {
        var total = urls.length, ok = 0, fail = 0;
        for (var i = 0; i < total; i++) {
            setBatch(total > 1 ? (i+1)+"/"+total : "");
            setStatus("解析中…" + (total > 1 ? " ("+(i+1)+"/"+total+")" : ""));
            setProgress(0);
            try {
                var info = getVideoInfo(urls[i]);
                var fp   = uniquePath(savePath, info.title);
                setStatus("下载: " + info.title);
                var size = downloadVideo(info.url, fp, function (d, t) {
                    if (t > 0) {
                        setProgress(d / t * 100);
                        setStatus("下载中: "+(d/1048576).toFixed(1)+" / "+(t/1048576).toFixed(1)+" MB");
                    }
                });
                addHistory("✓  "+new File(fp).getName()+"  ("+(size/1048576).toFixed(1)+" MB)", true);
                ok++;
            } catch (e) {
                addHistory("✗  "+urls[i].substring(0,40)+"  "+(e.message||"").substring(0,40), false);
                fail++;
            }
        }
        setProgress(100);
        setStatus(total===1 ? (ok?"下载完成！":"下载失败") : "完成："+ok+" 成功"+(fail?" "+fail+" 失败":""));
        setBatch("");
        ui.run(function () {
            ui.dlBtn.setText("开  始  下  载"); ui.dlBtn.setEnabled(true);
            if (ok > 0) ui.urlInput.setText("");
        });
        downloading = false;
    });
}

// ─── 自动采集核心（整个函数在子线程中运行，可直接 sleep / dialog）─────────────
function beginAutoCollect() {
    if (!hasAccessibility()) {
        addLog("✗ 无障碍服务未开启，采集终止");
        dialogs.alert("权限不足", "请先开启无障碍服务（在权限配置行点击 未开启 → ）");
        return;
    }

    autoRunning  = true;
    collectCount = 0;
    updateAutoUI(true);
    console.show();
    console.clear();
    addLog("━━ 采集启动 ━━");
    showOnePixelForeground();  // 1像素前台保活（华为可读剪贴板）
    setupClipboardMonitor();   // 剪贴板变化监听（备用）

    if (hasFloatWindow()) {
        showFloatStopBtn();
        addLog("● 悬浮停止按钮已显示");
    } else {
        addLog("⚠ 无悬浮窗权限，停止时请切回本 App");
        toast("未授予悬浮窗权限，停止时请切回本App点停止");
    }

    addLog("▶ 正在启动抖音…");
    app.launch(DOUYIN_PKG);
    sleep(2500);
    addLog("▶ 抖音已启动，开始采集循环");
    toast("自动采集已开始，脚本运行中…");

    while (autoRunning) {
        try {
            addLog("→ 寻找分享按钮…");
            var url = collectOneVideo();
            if (url) {
                var cnt = ++collectCount;
                addLog("✓ 第 " + cnt + " 个链接: " + url.substring(0, 50) + "…");
                ui.run(function () { ui.collectLabel.setText(String(cnt)); });
                setAutoDetail("第 " + cnt + " 个已加入下载队列");
                enqueueAutoDownload(url);
            }
        } catch (e) {
            addLog("✗ " + (e.message || String(e)));
            setAutoDetail("跳过（" + e.message + "）");
        }
        if (!autoRunning) break;
        addLog("↕ 上滑切换视频");
        doSwipeUp();
        sleep(2500);
    }
    addLog("━━ 采集已停止 ━━");
    sleep(800);
    console.hide();
}

function stopAutoCollect() {
    autoRunning = false;
    if (autoThread) { try { autoThread.interrupt(); } catch (e) {} autoThread = null; }
    hideFloatStopBtn();
    hideOnePixelForeground();  // 移除1像素保活窗口
    updateAutoUI(false);
    toast("采集已停止");
}

function updateAutoUI(running) {
    ui.run(function () {
        ui.autoStatusDot.setTextColor(Color.parseColor(running ? "#4CAF50" : "#333333"));
        ui.autoStatusLabel.setText(running ? "  采集运行中" : "  采集未运行");
        ui.autoStatusLabel.setTextColor(Color.parseColor(running ? "#EEEEEE" : "#888888"));
        ui.autoStartBtn.setEnabled(!running);
        ui.autoStopBtn.setEnabled(running);
        if (!running) setAutoDetail("就绪");
    });
}

// ─── 采集单个视频 ─────────────────────────────────────────────────────────────
function collectOneVideo() {
    var shareBtn = findShareButton();
    if (!shareBtn) throw new Error("未找到分享按钮");

    // 直播页：节点存在但不可见，跳过
    if (typeof shareBtn.visibleToUser === "function") {
        try {
            if (!shareBtn.visibleToUser()) throw new Error("分享按钮不可见（直播页），跳过");
        } catch (e) {
            if (String(e.message).indexOf("跳过") !== -1) throw e;
        }
    }

    addLog("→ 点击分享按钮");
    shareBtn.click();
    sleep(1200);

    var copyBtn = findCopyLinkBtn();
    if (!copyBtn) { back(); sleep(400); throw new Error("分享面板未找到复制链接按钮"); }

    lastClipText = "";
    addLog("→ 点击复制链接");
    copyBtn.click();
    sleep(600);   // 等抖音写入剪贴板

    // 读取链接（含华为前台切换兼容）
    var clip = readClipCompat();
    addLog("→ 链接: " + (clip || "(空)").substring(0, 60));
    if (!clip || !/https?:\/\//i.test(clip)) {
        back(); sleep(300);
        throw new Error("未获取到有效链接");
    }

    // 确保分享面板已关闭（App 切换后面板通常自动收起，但保险起见）
    if (textContains("复制链接").exists() || textContains("分享链接").exists()) {
        back(); sleep(300);
    }
    return clip;
}

// ─── 1像素前台保活（骗系统认为脚本在前台，华为可读剪贴板）────────────────────
function showOnePixelForeground() {
    if (onePixelView) return;
    ui.run(function () {
        try {
            var WLP  = android.view.WindowManager.LayoutParams;
            var wm   = activity.getSystemService(android.content.Context.WINDOW_SERVICE);
            var lp   = new WLP(
                1, 1,                                    // 宽高 1px
                WLP.TYPE_APPLICATION_OVERLAY,            // 系统级浮层
                WLP.FLAG_NOT_TOUCHABLE |                 // 触摸穿透，不影响下面 App
                WLP.FLAG_NOT_TOUCH_MODAL,                // 模态外触摸也穿透
                // ★ 不加 FLAG_NOT_FOCUSABLE：让此窗口持有焦点 → 系统认为在前台
                android.graphics.PixelFormat.TRANSLUCENT
            );
            lp.gravity = android.view.Gravity.LEFT | android.view.Gravity.TOP;
            lp.x = 0; lp.y = 0;
            onePixelView = new android.view.View(activity);
            wm.addView(onePixelView, lp);
            addLog("● 1像素前台窗口已激活");
        } catch (e) {
            addLog("1像素窗口失败: " + e.message);
        }
    });
    sleep(200);
}

function hideOnePixelForeground() {
    if (!onePixelView) return;
    ui.run(function () {
        try {
            var wm = activity.getSystemService(android.content.Context.WINDOW_SERVICE);
            wm.removeView(onePixelView);
        } catch (e) {}
        onePixelView = null;
    });
}

// 读剪贴板：1像素窗口保活后直接读，降级走监听器或 Activity 切换
function readClipCompat() {
    // 1像素窗口使进程持有焦点，getClip() 应可直接成功
    try {
        var clip = getClip() || "";
        if (clip && /https?:\/\//.test(clip)) return clip;
    } catch (e) {}

    // 监听器备用
    if (lastClipText && /https?:\/\//.test(lastClipText)) return lastClipText;

    // 最终降级：把 Activity 切到前台读（有画面切换）
    addLog("→ 降级：Activity 切到前台读剪贴板");
    try {
        var intent = new android.content.Intent(auto.service, activity.getClass());
        intent.addFlags(android.content.Intent.FLAG_ACTIVITY_REORDER_TO_FRONT |
                        android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
        auto.service.startActivity(intent);
        sleep(500);
        var clip2 = getClip() || "";
        app.launch(DOUYIN_PKG);
        sleep(1500);
        if (clip2) return clip2;
    } catch (e) { addLog("→ Activity 切换失败: " + e.message); }

    return "";
}

// 找"复制链接 / 分享链接"按钮，找不到则左划一次重试
function findCopyLinkBtn() {
    var btn = textContains("复制链接").findOne(1200) ||
              descContains("复制链接").findOne(400)  ||
              textContains("分享链接").findOne(400)  ||
              descContains("分享链接").findOne(400);
    if (btn) return btn;
    addLog("→ 首屏无按钮，左划分享面板");
    var w = device.width, h = device.height;
    swipe(Math.round(w * 0.85), Math.round(h * 0.88),
          Math.round(w * 0.15), Math.round(h * 0.88), 300);
    sleep(600);
    return textContains("复制链接").findOne(1000) ||
           descContains("复制链接").findOne(300)  ||
           textContains("分享链接").findOne(300)  ||
           descContains("分享链接").findOne(300)  || null;
}

function findShareButton() {
    var selectors = [
        // 精确 resource-id（抖音主版本）
        function () { return id("com.ss.android.ugc.aweme:id/share_container").findOne(800); },
        // 降级：内容描述
        function () { return desc("分享").findOne(600); },
        function () { return descContains("分享").findOne(600); }
    ];
    for (var i = 0; i < selectors.length; i++) {
        try { var b = selectors[i](); if (b) return b; } catch (e) {}
    }
    // 兜底坐标点击：右侧 93%，高度 72%
    var w = device.width, h = device.height;
    click(Math.round(w * 0.93), Math.round(h * 0.72));
    sleep(700);
    if (textContains("分享链接").exists()) return { click: function () {} };
    return null;
}

function doSwipeUp() {
    var w = device.width, h = device.height;
    swipe(Math.round(w * 0.5), Math.round(h * 0.75), Math.round(w * 0.5), Math.round(h * 0.25), 350);
}

// ─── API 采集（WebView 登录 + 直接调抖音 Web 接口）────────────────────────────
var douyinCookie    = "";
var douyinWinRef    = null;
var douyinWv        = null;   // WebView 保活引用，登录后用于 API 调用
var pullFeedRunning = false;  // 防止并发重入
var feedPaused      = false;  // 暂停标志（采集 + 下载均暂停）

// 按钮事件
ui.apiLoginBtn.on("click", function () {
    if (douyinWinRef) { toast("登录窗口已打开"); return; }
    ui.post(function () { openLoginWebView(); });
});
ui.apiFeedBtn.on("click", function () {
    if (pullFeedRunning) { toast("采集中，请使用浮层停止按钮"); return; }
    if (!douyinWv) { toast("请先登录抖音账号"); return; }
    var n   = parseInt(ui.apiFeedCount.getText().toString()) || 20;
    var tab = ui.apiFeedTab.getSelectedItem().toString();
    feedPaused = false;
    ui.apiFeedBtn.setEnabled(false);
    ui.apiFeedBtn.setText("采集中…");
    pullFeedVideos(n, tab);
});
ui.clearCollectLogBtn.on("click", function () {
    _collectLines = [];
    try { ui.collectLogTv.setText(""); } catch (e) {}
});
ui.clearDownloadLogBtn.on("click", function () {
    _downloadLines = [];
    try { ui.downloadLogTv.setText(""); } catch (e) {}
});
ui.apiUserBtn.on("click", function () {
    var url = ui.apiUserUrl.getText().toString().trim();
    if (!url) { toast("请输入用户主页链接"); return; }
    pullUserVideos(url, 100);
});

// ─── 采集浮层（暂停/继续/停止 悬浮控制面板）────────────────────────────────────
var _collectOverlay  = null;   // WindowManager 中的浮层根布局
var _overlayStat     = null;   // 状态 TextView
var _overlayPauseBtn = null;   // 暂停/继续按钮

function showCollectOverlay(tab) {
    if (_collectOverlay) return;
    // 必须在 UI 主线程创建和添加 View
    ui.run(function () {
        try {
            var ctx = activity;
            var WLP = android.view.WindowManager.LayoutParams;
            var LL  = android.widget.LinearLayout;
            var WRAP = LL.LayoutParams.WRAP_CONTENT;

            var root = new LL(ctx);
            root.setOrientation(LL.VERTICAL);
            root.setBackgroundColor(android.graphics.Color.parseColor("#E8111111"));
            var pad = dpToPx(12);
            root.setPadding(pad, pad, pad, pad);

            // ── 标题行 ──
            var titleRow = new LL(ctx);
            titleRow.setOrientation(LL.HORIZONTAL);
            titleRow.setGravity(android.view.Gravity.CENTER_VERTICAL);
            titleRow.setLayoutParams(new LL.LayoutParams(WRAP, WRAP));

            var dot = new android.widget.TextView(ctx);
            dot.setText("● ");
            dot.setTextColor(android.graphics.Color.parseColor("#4CAF50"));
            dot.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 11);
            titleRow.addView(dot);

            var title = new android.widget.TextView(ctx);
            title.setText("【" + tab + "】采集中");
            title.setTextColor(android.graphics.Color.WHITE);
            title.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 12);
            title.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
            titleRow.addView(title);
            root.addView(titleRow);

            // ── 状态文字 ──
            _overlayStat = new android.widget.TextView(ctx);
            _overlayStat.setText("启动中…");
            _overlayStat.setTextColor(android.graphics.Color.parseColor("#AAAAAA"));
            _overlayStat.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 10);
            _overlayStat.setPadding(0, dpToPx(4), 0, dpToPx(8));
            root.addView(_overlayStat);

            // ── 按钮行 ──
            var btnRow = new LL(ctx);
            btnRow.setOrientation(LL.HORIZONTAL);

            _overlayPauseBtn = new android.widget.Button(ctx);
            _overlayPauseBtn.setText("暂停");
            _overlayPauseBtn.setTextColor(android.graphics.Color.WHITE);
            _overlayPauseBtn.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 12);
            _overlayPauseBtn.setBackgroundColor(android.graphics.Color.parseColor("#555555"));
            _overlayPauseBtn.setLayoutParams(new LL.LayoutParams(0, dpToPx(40), 1));
            btnRow.addView(_overlayPauseBtn);

            var gap = new android.view.View(ctx);
            gap.setLayoutParams(new LL.LayoutParams(dpToPx(8), 1));
            btnRow.addView(gap);

            var stopBtn = new android.widget.Button(ctx);
            stopBtn.setText("停止");
            stopBtn.setTextColor(android.graphics.Color.WHITE);
            stopBtn.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 12);
            stopBtn.setBackgroundColor(android.graphics.Color.parseColor("#FF4444"));
            stopBtn.setLayoutParams(new LL.LayoutParams(0, dpToPx(40), 1));
            btnRow.addView(stopBtn);

            root.addView(btnRow);

            // ── 加入 WindowManager ──
            var wm = ctx.getSystemService(android.content.Context.WINDOW_SERVICE);
            var lp = new WLP(dpToPx(240), WRAP,
                WLP.TYPE_APPLICATION_OVERLAY,
                WLP.FLAG_NOT_TOUCH_MODAL | WLP.FLAG_NOT_FOCUSABLE,
                android.graphics.PixelFormat.TRANSLUCENT);
            lp.gravity = android.view.Gravity.TOP | android.view.Gravity.RIGHT;
            lp.x = dpToPx(8); lp.y = dpToPx(72);
            wm.addView(root, lp);
            _collectOverlay = root;

            // ── 按钮事件（已在主线程，直接 setOnClickListener）──
            _overlayPauseBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
                onClick: function () {
                    feedPaused = !feedPaused;
                    _overlayPauseBtn.setText(feedPaused ? "继续" : "暂停");
                    _overlayPauseBtn.setBackgroundColor(android.graphics.Color.parseColor(
                        feedPaused ? "#FF8C00" : "#555555"));
                }
            }));
            stopBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
                onClick: function () {
                    pullFeedRunning = false;
                    feedPaused = false;
                }
            }));
        } catch (e) {
            addLog("浮层创建失败: " + e.message);
        }
    });
}

function updateCollectOverlay(msg) {
    if (!_overlayStat) return;
    // _overlayStat.post 本身是 UI 线程安全的
    try {
        var _s = _overlayStat;
        _s.post(new JavaAdapter(java.lang.Runnable, {
            run: function () { try { _s.setText(msg); } catch (e) {} }
        }));
    } catch (e) {}
}

function hideCollectOverlay() {
    if (!_collectOverlay) return;
    // 必须在 UI 主线程移除 View
    ui.run(function () {
        try {
            var wm = activity.getSystemService(android.content.Context.WINDOW_SERVICE);
            wm.removeView(_collectOverlay);
        } catch (e) {}
        _collectOverlay  = null;
        _overlayStat     = null;
        _overlayPauseBtn = null;
    });
}

// 打开 WebView 登录窗口
function openLoginWebView() {
    try {
        var ctx = activity;
        var WLP = android.view.WindowManager.LayoutParams;
        var LL  = android.widget.LinearLayout;
        var MATCH = LL.LayoutParams.MATCH_PARENT;
        var WRAP  = LL.LayoutParams.WRAP_CONTENT;

        // ── 根布局（垂直，黑底） ──
        var root = new LL(ctx);
        root.setOrientation(LL.VERTICAL);
        root.setBackgroundColor(android.graphics.Color.BLACK);

        // ── 工具栏 ──
        var toolbar = new LL(ctx);
        toolbar.setOrientation(LL.HORIZONTAL);
        toolbar.setBackgroundColor(android.graphics.Color.parseColor("#1A1A1A"));
        toolbar.setGravity(android.view.Gravity.CENTER_VERTICAL);
        toolbar.setPadding(12, 0, 12, 0);
        toolbar.setLayoutParams(new LL.LayoutParams(MATCH, 132));

        // 后退按钮
        var btnBack = _mkToolBtn(ctx, "‹", "#DDDDDD");
        toolbar.addView(btnBack);

        // 刷新按钮
        var btnRefresh = _mkToolBtn(ctx, "↺", "#DDDDDD");
        toolbar.addView(btnRefresh);

        // URL 显示
        var urlTv = new android.widget.TextView(ctx);
        urlTv.setText("www.douyin.com");
        urlTv.setTextColor(android.graphics.Color.parseColor("#888888"));
        urlTv.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 10);
        urlTv.setSingleLine(true);
        urlTv.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
        urlTv.setLayoutParams(new LL.LayoutParams(0, WRAP, 1));
        urlTv.setPadding(16, 0, 16, 0);
        toolbar.addView(urlTv);

        // 登录状态提示
        var loginHint = new android.widget.TextView(ctx);
        loginHint.setText("登录后自动关闭");
        loginHint.setTextColor(android.graphics.Color.parseColor("#555555"));
        loginHint.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 9);
        loginHint.setPadding(0, 0, 16, 0);
        toolbar.addView(loginHint);

        // 关闭按钮
        var btnClose = _mkToolBtn(ctx, "✕", "#FF4444");
        toolbar.addView(btnClose);
        root.addView(toolbar);

        // ── 进度条 ──
        var progress = new android.widget.ProgressBar(
            ctx, null, android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);
        progress.setProgress(0);
        progress.setLayoutParams(new LL.LayoutParams(MATCH, 6));
        root.addView(progress);

        // ── WebView ──
        var wv = new android.webkit.WebView(ctx);
        wv.setLayoutParams(new LL.LayoutParams(MATCH, 0, 1));
        var ws = wv.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setUserAgentString(PC_UA);
        try { ws.setMixedContentMode(0); } catch(e) {}
        root.addView(wv);

        // ── WebChromeClient：进度条 ──
        wv.setWebChromeClient(new JavaAdapter(android.webkit.WebChromeClient, {
            onProgressChanged: function(view, p) {
                ui.run(function() { progress.setProgress(p); });
            }
        }));

        // ── WebViewClient：URL 显示 + 登录检测 ──
        wv.setWebViewClient(new JavaAdapter(android.webkit.WebViewClient, {
            onPageStarted: function(view, url, favicon) {
                ui.run(function() { urlTv.setText(url || ""); });
            },
            onPageFinished: function(view, url) {
                ui.run(function() { urlTv.setText(url || ""); });
                threads.start(function() {
                    if (douyinWv) return;   // 防止 onPageFinished 多次触发重复处理
                    sleep(800);
                    var ck = android.webkit.CookieManager.getInstance()
                                 .getCookie("https://www.douyin.com") || "";
                    if (ck.indexOf("sessionid") !== -1) {
                        douyinCookie = ck;
                        douyinWv = wv;   // 标记已处理（防重入）
                        // ★ 关键：跳回主站，确保后续 fetch 是同源请求（不被 CORS 拦截）
                        ui.run(function() { wv.loadUrl("https://www.douyin.com/"); });
                        sleep(3000);   // 等主页加载完成
                        ui.run(function() {
                            ui.apiLoginStatus.setText("已登录 ✓");
                            ui.apiLoginStatus.setTextColor(Color.parseColor("#4CAF50"));
                            // 将窗口缩成 1×1 不可见，保留 WebView 上下文（含 Cookie/Session）
                            try {
                                var wm2 = ctx.getSystemService(android.content.Context.WINDOW_SERVICE);
                                var miniLp = new WLP(1, 1,
                                    WLP.TYPE_APPLICATION_OVERLAY,
                                    WLP.FLAG_NOT_FOCUSABLE | WLP.FLAG_NOT_TOUCHABLE | WLP.FLAG_NOT_TOUCH_MODAL,
                                    android.graphics.PixelFormat.TRANSLUCENT);
                                miniLp.gravity = android.view.Gravity.TOP | android.view.Gravity.LEFT;
                                wm2.updateViewLayout(root, miniLp);
                                root.setVisibility(android.view.View.INVISIBLE);
                            } catch(e2) {}
                        });
                        toast("抖音登录成功！");
                        addLog("● WebView 已保活（www.douyin.com），API 采集就绪");
                    }
                });
            }
        }));
        wv.loadUrl("https://www.douyin.com");

        // ── 加入 WindowManager
        // 高度留出底部导航/手势区（120px），不遮挡系统 Home 手势
        var wm = ctx.getSystemService(android.content.Context.WINDOW_SERVICE);
        var winH = device.height - 120;
        var lp = new WLP(
            MATCH, winH,
            WLP.TYPE_APPLICATION_OVERLAY,
            WLP.FLAG_NOT_TOUCH_MODAL,   // 窗口外触摸穿透 → Home/系统手势不受影响
            android.graphics.PixelFormat.TRANSLUCENT
        );
        lp.gravity = android.view.Gravity.TOP;
        wm.addView(root, lp);
        douyinWinRef = root;

        // ── 按钮事件 ──
        btnBack.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
            onClick: function() { if (wv.canGoBack()) wv.goBack(); }
        }));
        btnRefresh.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
            onClick: function() { wv.reload(); }
        }));
        btnClose.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
            onClick: function() { closeDyWin(root); }
        }));

    } catch(e) {
        toast("打开登录窗口失败: " + e.message);
        log("openLoginWebView error: " + e);
    }
}

// 工具栏按钮生成
function _mkToolBtn(ctx, label, color) {
    var btn = new android.widget.TextView(ctx);
    btn.setText(label);
    btn.setTextColor(android.graphics.Color.parseColor(color));
    btn.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 18);
    btn.setPadding(20, 0, 20, 0);
    btn.setGravity(android.view.Gravity.CENTER);
    btn.setLayoutParams(new android.widget.LinearLayout.LayoutParams(
        android.widget.LinearLayout.LayoutParams.WRAP_CONTENT, 132));
    return btn;
}

function closeDyWin(root) {
    ui.run(function() {
        try {
            activity.getSystemService(android.content.Context.WINDOW_SERVICE).removeView(root);
        } catch(e) {}
        douyinWinRef = null;
        douyinWv     = null;
        douyinCookie = "";
        ui.apiLoginStatus.setText("未登录");
        ui.apiLoginStatus.setTextColor(Color.parseColor("#FF5252"));
    });
}

// ── WebView 内部 fetch（同源，无需 X-Bogus，Cookie 自动携带）──────────────────
// 在已登录的 WebView 页面里注入 fetch，轮询结果
function wvApiGet(path) {
    if (!douyinWv) throw new Error("请先登录抖音账号（API采集需要WebView登录）");
    var rid = "_ar" + Date.now();
    var fetchUrl = path.startsWith("http") ? path : ("https://www.douyin.com" + path);
    var safeUrl = fetchUrl.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
    // 用 r.text() 拿原始响应体，再手动 JSON.parse，失败时把 HTTP 状态码和前120字符打日志
    var js =
        "(function(){" +
        "window['" + rid + "']=null;" +
        "fetch('" + safeUrl + "',{credentials:'include'})" +
        ".then(function(resp){" +
        "  var st=resp.status;" +
        "  return resp.text().then(function(t){" +
        "    try{window['" + rid + "']='__OK__'+JSON.stringify(JSON.parse(t))}" +
        "    catch(e){window['" + rid + "']='__RAW__'+st+'__'+t.substring(0,150)}" +
        "  });" +
        "})" +
        ".catch(function(e){window['" + rid + "']='__ERR__'+e.message});" +
        "})()";
    ui.run(function() { douyinWv.evaluateJavascript(js, null); });
    sleep(500);

    // 轮询（最长 18 s）
    for (var i = 0; i < 60; i++) {
        sleep(300);
        var h = {val: null, ready: false};
        var _h = h;
        ui.run(function() {
            douyinWv.evaluateJavascript(
                "(function(){return window['" + rid + "'];})()",
                new JavaAdapter(android.webkit.ValueCallback, {
                    onReceiveValue: function(v) { _h.val = v; _h.ready = true; }
                })
            );
        });
        for (var j = 0; j < 20 && !_h.ready; j++) sleep(50);

        var raw = String(_h.val || "");
        if (raw && raw !== "null") {
            if (raw.charAt(0) === '"') raw = JSON.parse(raw);  // evaluateJavascript 对字符串 JSON 编码，反转义
            if (raw.indexOf("__ERR__") === 0)  throw new Error("Fetch 失败: " + raw.substring(7));
            if (raw.indexOf("__RAW__") === 0) {
                // 非 JSON 响应：打出 HTTP 状态码和原始预览
                var rest = raw.substring(7);
                var sep  = rest.indexOf("__");
                var status  = rest.substring(0, sep);
                var preview = rest.substring(sep + 2);
                throw new Error("HTTP " + status + " 非JSON响应: " + preview);
            }
            if (raw.indexOf("__OK__") === 0) return JSON.parse(raw.substring(6));
        }
    }
    throw new Error("API 请求超时");
}

// ── 导航式 API 请求（loadUrl → document.body.innerText，绝对同源，无 CORS 问题）────
// 比 wvApiGet 更可靠，但会改变 WebView 当前页，调用后自动跳回 www.douyin.com
function wvNavGet(path) {
    if (!douyinWv || !douyinWinRef) throw new Error("WebView未就绪，请先登录");
    var fullUrl = path.startsWith("http") ? path : ("https://www.douyin.com" + path);
    var result = {raw: null, done: false};
    var _r = result;
    ui.run(function() {
        douyinWv.setWebViewClient(new JavaAdapter(android.webkit.WebViewClient, {
            onPageFinished: function(view, url) {
                // 先把 client 换回空的，防止后续导航又触发
                view.setWebViewClient(new JavaAdapter(android.webkit.WebViewClient, {}));
                view.evaluateJavascript("document.body.innerText",
                    new JavaAdapter(android.webkit.ValueCallback, {
                        onReceiveValue: function(v) { _r.raw = v; _r.done = true; }
                    })
                );
            }
        }));
        douyinWv.loadUrl(fullUrl);
    });
    for (var i = 0; i < 60 && !_r.done; i++) sleep(300);
    // 导航完成后跳回主页（保证下次 fetch 仍在同源）
    ui.run(function() { douyinWv.loadUrl("https://www.douyin.com/"); });
    if (!_r.done) throw new Error("导航请求超时");
    var raw = String(_r.raw || "");
    if (!raw || raw === "null") throw new Error("响应为空");
    if (raw.charAt(0) === '"') raw = JSON.parse(raw);   // evaluateJavascript 反转义
    addLog("响应前80字: " + raw.substring(0, 80));
    if (raw.charAt(0) !== '{' && raw.charAt(0) !== '[')
        throw new Error("非JSON响应: " + raw.substring(0, 80));
    return JSON.parse(raw);
}

// 从 WebView 的 Douyin JS 环境里生成 X-Bogus 签名（_byted_acrawler.sign）
function wvGetXBogus(queryUrl) {
    if (!douyinWv) return "";
    var safe = queryUrl.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
    var js =
        "(function(){" +
        "try{" +
        "  var c=window._byted_acrawler||window.byted_acrawler;" +
        "  if(c&&c.sign)return String(c.sign({url:'" + safe + "'}))" +
        "}catch(e){}" +
        "return ''" +
        "})()";
    var h = {v: null, d: false};
    var _h = h;
    ui.run(function() {
        douyinWv.evaluateJavascript(js, new JavaAdapter(android.webkit.ValueCallback, {
            onReceiveValue: function(v) { _h.v = v; _h.d = true; }
        }));
    });
    for (var k = 0; k < 20 && !_h.d; k++) sleep(100);
    if (!_h.v) return "";
    var raw = String(_h.v);
    if (raw.charAt(0) === '"') { try { raw = JSON.parse(raw); } catch(e) {} }
    return (raw === "null" || raw === "undefined" || raw === "") ? "" : raw;
}

// Cookie + X-Bogus 直接 HTTP 请求（与 PC 浏览器抓 cookie 的方式完全相同）
function dyApiGet(path) {
    if (!douyinCookie) throw new Error("请先登录抖音账号");
    var base = "https://www.douyin.com" + path;
    // 从 WebView 拿 X-Bogus（_byted_acrawler.sign），签名失败就裸请求
    var xb = wvGetXBogus(base);
    var url = xb ? base + (base.indexOf("?") >= 0 ? "&" : "?") + "X-Bogus=" + xb : base;
    addLog((xb ? "✓ X-Bogus" : "⚠ 无X-Bogus") + "  " + path.substring(0, 55));
    var resp = http.get(url, {
        headers: {
            "Cookie":          douyinCookie,
            "User-Agent":      PC_UA,
            "Referer":         "https://www.douyin.com/",
            "Accept":          "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "identity",
            "Sec-Fetch-Dest":  "empty",
            "Sec-Fetch-Mode":  "cors",
            "Sec-Fetch-Site":  "same-origin"
        }
    });
    var body = resp.body.string();
    addLog("HTTP " + resp.statusCode + "  " + body.substring(0, 120));
    if (resp.statusCode !== 200) throw new Error("HTTP " + resp.statusCode);
    return JSON.parse(body);
}

// ── 精选采集：同时 hook fetch + XHR，拦截所有含 aweme_id 的 API 响应 ─────────
var _FETCH_HOOK =
    "(function(){" +
    "if(window._dy_h)return;" +
    "window._dy_h=1;" +
    "window._dy_ids=window._dy_ids||[];" +
    "window._dy_urls=window._dy_urls||[];" +  // 用于调试：记录最近捕获的 URL
    // ── fetch hook ──
    "var _F=window.fetch;" +
    "if(_F){window.fetch=function(){" +
    "  var a=arguments;" +
    "  return _F.apply(this,a).then(function(r){" +
    "    var u=String(typeof a[0]==='string'?a[0]:((a[0]||{}).url||''));" +
    "    if(window._dy_urls.indexOf(u.substring(0,60))<0)window._dy_urls.push(u.substring(0,60));" +
    "    if(u.indexOf('aweme')>=0){" +
    "      r.clone().json().then(function(d){" +
    "        (d.aweme_list||[]).forEach(function(v){" +
    "          if(v&&v.aweme_id&&window._dy_ids.indexOf(v.aweme_id)<0)" +
    "            window._dy_ids.push(v.aweme_id)" +
    "        });" +
    "        if(Array.isArray(d.data))d.data.forEach(function(x){" +
    "          var id=((x.aweme_info||x).aweme_id)||'';" +
    "          if(id&&window._dy_ids.indexOf(id)<0)window._dy_ids.push(id)" +
    "        })" +
    "      }).catch(function(){})" +
    "    };return r" +
    "  })" +
    "};}" +
    // ── XHR hook ──
    "var _XO=XMLHttpRequest.prototype.open;" +
    "var _XS=XMLHttpRequest.prototype.send;" +
    "XMLHttpRequest.prototype.open=function(m,u){" +
    "  this._dy_u=String(u||'');" +
    "  if(window._dy_urls.indexOf(this._dy_u.substring(0,60))<0)" +
    "    window._dy_urls.push(this._dy_u.substring(0,60));" +
    "  return _XO.apply(this,arguments);" +
    "};" +
    "XMLHttpRequest.prototype.send=function(){" +
    "  var xhr=this,orig=xhr.onreadystatechange;" +
    "  xhr.onreadystatechange=function(){" +
    "    if(xhr.readyState===4&&xhr._dy_u&&xhr._dy_u.indexOf('aweme')>=0){" +
    "      try{var d=JSON.parse(xhr.responseText);" +
    "        (d.aweme_list||[]).forEach(function(v){" +
    "          if(v&&v.aweme_id&&window._dy_ids.indexOf(v.aweme_id)<0)" +
    "            window._dy_ids.push(v.aweme_id)" +
    "        });" +
    "        if(Array.isArray(d.data))d.data.forEach(function(x){" +
    "          var id=((x.aweme_info||x).aweme_id)||'';" +
    "          if(id&&window._dy_ids.indexOf(id)<0)window._dy_ids.push(id)" +
    "        })" +
    "      }catch(e){}}" +
    "    if(orig)orig.apply(this,arguments);" +
    "  };" +
    "  return _XS.apply(this,arguments);" +
    "};" +
    "})()";

// 点击精选 Tab（文字匹配，无子节点的叶节点）
var _CLICK_JINGXUAN =
    "(function(){" +
    "var all=document.querySelectorAll('*');" +
    "for(var i=0;i<all.length;i++){" +
    "  var el=all[i];" +
    "  if(el.childElementCount===0&&(el.textContent||'').trim()==='精选')" +
    "    {el.click();return 'ok:'+el.tagName}" +
    "}" +
    "return 'notfound'" +
    "})()";

// 读取已收集的 ID
var _POLL_IDS = "(function(){return JSON.stringify(window._dy_ids||[])})()";

// 直接从 DOM 链接提取视频 ID（作为 fetch hook 的补充/后备）
var _SCRAPE_IDS =
    "(function(){" +
    "var ids=[];" +
    "var links=document.querySelectorAll('a[href]');" +
    "for(var i=0;i<links.length;i++){" +
    "  var m=(links[i].getAttribute('href')||'').match(/\\/video\\/(\\d{10,})/);" +
    "  if(m&&ids.indexOf(m[1])<0)ids.push(m[1]);" +
    "}" +
    "return JSON.stringify(ids);" +
    "})()";

// 调试：读取 hook 状态和捕获的 URL 列表
var _DEBUG_STATE =
    "(function(){" +
    "return JSON.stringify({" +
    "  h:window._dy_h," +
    "  ids:(window._dy_ids||[]).length," +
    "  urls:(window._dy_urls||[]).slice(0,5)," +
    "  rs:document.readyState" +
    "});" +
    "})()";

// 打开专用采集窗口：抖音页面 + fetch-hook 拦截
// 精选采集：复用已登录 WebView，注入 _FETCH_HOOK 拦截页面自己的 API 请求
// 无需新窗口，无需手动找 API 端点，无需 X-Bogus
function pullFeedVideos(count, tab) {
    tab = tab || "推荐";
    if (pullFeedRunning) { toast("采集进行中，请稍候…"); return; }
    if (!douyinWv)      { toast("请先在【自动采集】Tab 登录抖音账号"); return; }
    pullFeedRunning = true;

    threads.start(function () {
        var totalAdded = 0;
        var loopNum    = 0;
        var WLP = android.view.WindowManager.LayoutParams;
        var wm  = activity.getSystemService(android.content.Context.WINDOW_SERVICE);
        var sw  = device.width, sh = device.height;

        var _SCROLL_JS =
            "(function(){" +
            "  var containers=[" +
            "    document.querySelector('#feedList')," +
            "    document.querySelector('.feed-container')," +
            "    document.querySelector('[class*=scroll]')," +
            "    document.querySelector('[class*=feed]')," +
            "    document.querySelector('[class*=swiper]')," +
            "    document.documentElement,document.body" +
            "  ];" +
            "  for(var i=0;i<containers.length;i++){" +
            "    var c=containers[i];" +
            "    if(c&&c.scrollHeight>c.clientHeight+10){c.scrollTop=c.scrollHeight;break;}" +
            "  }" +
            "  window.scrollTo(0,document.documentElement.scrollHeight||99999);" +
            "  window.dispatchEvent(new Event('scroll'));" +
            "  window.dispatchEvent(new TouchEvent('touchend'));" +
            "})()";

        // 生成点击指定 Tab 的 JS
        function makeClickTabJS(tabName) {
            var s = tabName.replace(/'/g, "\\'");
            return "(function(){var all=document.querySelectorAll('*');" +
                   "for(var i=0;i<all.length;i++){var el=all[i];" +
                   "if(el.childElementCount===0&&(el.textContent||'').trim()==='" + s + "')" +
                   "{el.click();return 'ok:'+el.tagName}}" +
                   "return 'notfound'})()";
        }

        // 采集浮层
        showCollectOverlay(tab);

        try {
            // WebView 展开为右下角小窗（约 1/2 宽 × 1/3 高），让页面正常渲染
            ui.run(function () {
                var wvW = Math.round(sw * 0.5);
                var wvH = Math.round(sh * 0.35);
                var lp = new WLP(wvW, wvH,
                    WLP.TYPE_APPLICATION_OVERLAY,
                    WLP.FLAG_NOT_FOCUSABLE | WLP.FLAG_NOT_TOUCHABLE | WLP.FLAG_NOT_TOUCH_MODAL,
                    android.graphics.PixelFormat.TRANSLUCENT);
                lp.gravity = android.view.Gravity.BOTTOM | android.view.Gravity.RIGHT;
                lp.x = 0; lp.y = 0;
                wm.updateViewLayout(douyinWinRef, lp);
                douyinWinRef.setVisibility(android.view.View.VISIBLE);
                douyinWv.setWebViewClient(new JavaAdapter(android.webkit.WebViewClient, {
                    onPageStarted: function (v, u, f) { v.evaluateJavascript(_FETCH_HOOK, null); },
                    onPageFinished: function (v, u)   { v.evaluateJavascript(_FETCH_HOOK, null); }
                }));
            });
            sleep(300);

            addCollectLog("▶ 【" + tab + "】循环采集启动，每批 " + count + " 个");

            // ════ 外层循环：每批采集 + 下载，直到用户点停止 ════
            while (pullFeedRunning) {
                // 暂停等待
                while (feedPaused && pullFeedRunning) { sleep(500); }
                if (!pullFeedRunning) break;

                loopNum++;
                addCollectLog("━━ 第 " + loopNum + " 批开始 ━━");

                // 重置 IDs，加载主页
                ui.run(function () {
                    douyinWv.evaluateJavascript("window._dy_ids=[];window._dy_h=0;window._dy_urls=[];", null);
                    douyinWv.loadUrl("https://www.douyin.com/");
                });
                addCollectLog("  加载页面…");
                // 等待页面加载，最多 12 秒，每秒检测 readyState
                for (var pw = 0; pw < 12 && pullFeedRunning; pw++) {
                    sleep(1000);
                    var rsR = {v: null, d: false}; var _rsR = rsR;
                    ui.run(function () {
                        douyinWv.evaluateJavascript("document.readyState",
                            new JavaAdapter(android.webkit.ValueCallback, {
                                onReceiveValue: function (v) { _rsR.v = v; _rsR.d = true; }
                            })
                        );
                    });
                    for (var rk = 0; rk < 10 && !_rsR.d; rk++) sleep(100);
                    var rs = String(_rsR.v || "");
                    if (rs.indexOf("complete") >= 0 && pw >= 4) break;
                }
                if (!pullFeedRunning) break;

                // 诊断：打印 hook 状态和已捕获信息
                var dbR = {v: null, d: false}; var _dbR = dbR;
                ui.run(function () {
                    douyinWv.evaluateJavascript(_DEBUG_STATE,
                        new JavaAdapter(android.webkit.ValueCallback, {
                            onReceiveValue: function (v) { _dbR.v = v; _dbR.d = true; }
                        })
                    );
                });
                for (var dk = 0; dk < 20 && !_dbR.d; dk++) sleep(100);
                var dbStr = String(_dbR.v || "");
                if (dbStr.charAt(0) === '"') try { dbStr = JSON.parse(dbStr); } catch(e) {}
                addCollectLog("  [状态] " + dbStr.substring(0, 150));

                // 点击指定频道 Tab
                if (tab !== "推荐") {
                    var cr = {v: null, d: false};
                    var _cr = cr;
                    ui.run(function () {
                        douyinWv.evaluateJavascript(makeClickTabJS(tab),
                            new JavaAdapter(android.webkit.ValueCallback, {
                                onReceiveValue: function (v) { _cr.v = v; _cr.d = true; }
                            })
                        );
                    });
                    for (var kc = 0; kc < 20 && !_cr.d; kc++) sleep(100);
                    var crr = String(_cr.v || "");
                    if (crr.charAt(0) === '"') try { crr = JSON.parse(crr); } catch(e) {}
                    addCollectLog("  点击[" + tab + "]: " + crr);
                    sleep(3000);
                    if (!pullFeedRunning) break;
                }

                // 内层：滚动 + 拦截 IDs（fetch hook + DOM 双路）
                var allIds   = [];
                var noNewCnt = 0;
                for (var t = 0; t < 30 && allIds.length < count && pullFeedRunning; t++) {
                    // 暂停等待
                    while (feedPaused && pullFeedRunning) { sleep(500); }
                    if (!pullFeedRunning) break;
                    // 重注入 hook（每轮确保已安装）
                    ui.run(function () {
                        douyinWv.evaluateJavascript("window._dy_h=0;" + _FETCH_HOOK, null);
                    });
                    sleep(200);
                    ui.run(function () {
                        douyinWv.evaluateJavascript(_SCROLL_JS, null);
                    });
                    sleep(2500);

                    // ① 读取 fetch hook 捕获的 IDs
                    var pr = {v: null, d: false};
                    var _pr = pr;
                    ui.run(function () {
                        douyinWv.evaluateJavascript(_POLL_IDS,
                            new JavaAdapter(android.webkit.ValueCallback, {
                                onReceiveValue: function (v) { _pr.v = v; _pr.d = true; }
                            })
                        );
                    });
                    for (var k = 0; k < 30 && !_pr.d; k++) sleep(100);

                    var ids = [];
                    if (_pr.v && _pr.v !== "null") {
                        var raw = String(_pr.v);
                        if (raw.charAt(0) === '"') try { raw = JSON.parse(raw); } catch (e) {}
                        try { ids = JSON.parse(raw) || []; } catch (e) {}
                    }

                    // ② DOM 抓取（页面上可见链接直接提取）
                    var srR = {v: null, d: false}; var _srR = srR;
                    ui.run(function () {
                        douyinWv.evaluateJavascript(_SCRAPE_IDS,
                            new JavaAdapter(android.webkit.ValueCallback, {
                                onReceiveValue: function (v) { _srR.v = v; _srR.d = true; }
                            })
                        );
                    });
                    for (var sk = 0; sk < 20 && !_srR.d; sk++) sleep(100);
                    if (_srR.v && _srR.v !== "null") {
                        var srRaw = String(_srR.v);
                        if (srRaw.charAt(0) === '"') try { srRaw = JSON.parse(srRaw); } catch (e) {}
                        var srIds = [];
                        try { srIds = JSON.parse(srRaw) || []; } catch (e) {}
                        for (var si = 0; si < srIds.length; si++) {
                            if (ids.indexOf(srIds[si]) < 0) ids.push(srIds[si]);
                        }
                    }

                    // ③ 合并到 allIds（累加，不替换）
                    var prevLen = allIds.length;
                    for (var mi = 0; mi < ids.length; mi++) {
                        if (allIds.indexOf(ids[mi]) < 0) allIds.push(ids[mi]);
                    }
                    if (allIds.length > prevLen) {
                        noNewCnt = 0;
                        addCollectLog("  t=" + t + " 已收集: " + allIds.length + " (hook:" + (ids.length) + " dom:" + (srIds ? srIds.length : 0) + ")");
                    } else {
                        noNewCnt++;
                        addCollectLog("  t=" + t + " 无新增(" + noNewCnt + ") 总:" + allIds.length);
                    }
                    if (allIds.length > 0 && noNewCnt >= 5) { addCollectLog("  无新增，结束本批"); break; }
                    // 全空时等更久再重试
                    if (allIds.length === 0 && noNewCnt >= 3) { addCollectLog("  页面可能未加载，等待…"); sleep(3000); }
                }

                // 加入下载队列
                var batchAdded = 0;
                for (var i = 0; i < allIds.length && batchAdded < count; i++) {
                    enqueueAutoDownload("https://www.douyin.com/video/" + allIds[i]);
                    batchAdded++;
                }
                totalAdded += batchAdded;
                var batchMsg = "第 " + loopNum + " 批完成 +" + batchAdded + " 个，累计 " + totalAdded + " 个";
                addCollectLog("━━ " + batchMsg + " ━━");
                updateCollectOverlay(batchMsg);
                if (batchAdded > 0) addDownloadLog("第 " + loopNum + " 批加入 " + batchAdded + " 个视频");

                if (batchAdded === 0) {
                    addCollectLog("⚠ 本批未采到任何视频，等 10s 后重试…");
                    sleep(10000);
                } else {
                    sleep(2000);
                }
            }

            addCollectLog("■ 循环采集已停止，共加入 " + totalAdded + " 个视频");
            toast(tab + " 采集停止，共加入 " + totalAdded + " 个");

        } catch (e) {
            var em = String(e.message || e);
            if (em.indexOf("Interrupt") < 0) addCollectLog("✗ 采集异常: " + em.substring(0, 100));
        } finally {
            feedPaused = false;
            pullFeedRunning = false;
            // 关闭浮层
            hideCollectOverlay();
            // 恢复 WebView 到 1×1 不可见
            ui.run(function () {
                try {
                    var miniLp = new WLP(1, 1,
                        WLP.TYPE_APPLICATION_OVERLAY,
                        WLP.FLAG_NOT_FOCUSABLE | WLP.FLAG_NOT_TOUCHABLE | WLP.FLAG_NOT_TOUCH_MODAL,
                        android.graphics.PixelFormat.TRANSLUCENT);
                    miniLp.gravity = android.view.Gravity.TOP | android.view.Gravity.LEFT;
                    miniLp.x = 0; miniLp.y = 0;
                    wm.updateViewLayout(douyinWinRef, miniLp);
                    douyinWinRef.setVisibility(android.view.View.INVISIBLE);
                } catch (e2) {}
                if (douyinWv) {
                    douyinWv.setWebViewClient(new JavaAdapter(android.webkit.WebViewClient, {}));
                    douyinWv.loadUrl("https://www.douyin.com/");
                }
                // 恢复开始采集按钮
                ui.apiFeedBtn.setText("开始采集");
                ui.apiFeedBtn.setBackgroundColor(Color.parseColor("#FF8C00"));
                ui.apiFeedBtn.setEnabled(true);
            });
        }
    });
}

function openJingxuanCollect(targetCount) {
    try {
        var ctx = activity;
        var WLP = android.view.WindowManager.LayoutParams;
        var LL  = android.widget.LinearLayout;
        var MATCH = LL.LayoutParams.MATCH_PARENT;
        var WRAP  = LL.LayoutParams.WRAP_CONTENT;
        var collecting = {done: false};

        // ── 根布局 ──
        var root = new LL(ctx);
        root.setOrientation(LL.VERTICAL);
        root.setBackgroundColor(android.graphics.Color.BLACK);

        // ── 状态栏 ──
        var bar = new LL(ctx);
        bar.setOrientation(LL.HORIZONTAL);
        bar.setBackgroundColor(android.graphics.Color.parseColor("#1A1A1A"));
        bar.setGravity(android.view.Gravity.CENTER_VERTICAL);
        bar.setPadding(16, 0, 16, 0);
        bar.setLayoutParams(new LL.LayoutParams(MATCH, 128));

        var statusTv = new android.widget.TextView(ctx);
        statusTv.setText("正在加载精选频道…");
        statusTv.setTextColor(android.graphics.Color.parseColor("#EEEEEE"));
        statusTv.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 11);
        statusTv.setLayoutParams(new LL.LayoutParams(0, WRAP, 1));
        bar.addView(statusTv);

        var doneBtn  = _mkToolBtn(ctx, "加入下载", "#FF8C00");
        var closeBtn = _mkToolBtn(ctx, "✕",      "#FF5252");
        bar.addView(doneBtn);
        bar.addView(closeBtn);
        root.addView(bar);

        // ── WebView ──
        var wv = new android.webkit.WebView(ctx);
        wv.setLayoutParams(new LL.LayoutParams(MATCH, 0, 1));
        var ws = wv.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setUserAgentString(PC_UA);
        try { ws.setMixedContentMode(0); } catch(e) {}
        root.addView(wv);

        // ── 加入 WindowManager ──
        var wm = ctx.getSystemService(android.content.Context.WINDOW_SERVICE);
        var lp = new WLP(MATCH, device.height - 120,
            WLP.TYPE_APPLICATION_OVERLAY, WLP.FLAG_NOT_TOUCH_MODAL,
            android.graphics.PixelFormat.TRANSLUCENT);
        lp.gravity = android.view.Gravity.TOP;
        wm.addView(root, lp);

        // ── WebViewClient：每次页面开始/完成都注入 hook ──
        wv.setWebViewClient(new JavaAdapter(android.webkit.WebViewClient, {
            onPageStarted: function (view, url, fav) {
                view.evaluateJavascript(_FETCH_HOOK, null);
            },
            onPageFinished: function (view, url) {
                view.evaluateJavascript(_FETCH_HOOK, null);
                threads.start(function () {
                    sleep(1500);
                    // 尝试点击精选 Tab
                    var cr = {v: null, d: false};
                    var _cr = cr;
                    ui.run(function () {
                        view.evaluateJavascript(_CLICK_JINGXUAN,
                            new JavaAdapter(android.webkit.ValueCallback, {
                                onReceiveValue: function (v) { _cr.v = v; _cr.d = true; }
                            })
                        );
                    });
                    for (var k = 0; k < 10 && !_cr.d; k++) sleep(200);
                    addLog("精选Tab: " + String(_cr.v));
                });
            }
        }));
        wv.loadUrl("https://www.douyin.com/");

        // ── 关闭窗口 ──
        function closeWin() {
            ui.run(function () { try { wm.removeView(root); } catch(e) {} });
        }

        // ── 完成采集，加入下载队列 ──
        function finishCollect(ids) {
            if (collecting.done) return;
            collecting.done = true;
            var added = 0;
            for (var j = 0; j < ids.length && added < targetCount; j++) {
                enqueueAutoDownload("https://www.douyin.com/video/" + ids[j]);
                added++;
                addLog("精选 #" + added + " " + ids[j]);
            }
            toast("精选已加入队列：" + added + " 个");
            closeWin();
        }

        // ── 后台轮询：每 500 ms 读一次 window._dy_ids ──
        threads.start(function () {
            console.show(); console.clear();
            addLog("▶ 精选采集窗口已打开，等抖音加载数据…");
            addLog("  数据由抖音自己的 JS 拉取，脚本拦截响应");
            for (var t = 0; t < 120 && !collecting.done; t++) {
                sleep(500);
                var pr = {v: null, d: false};
                var _pr = pr;
                ui.run(function () {
                    wv.evaluateJavascript(_POLL_IDS,
                        new JavaAdapter(android.webkit.ValueCallback, {
                            onReceiveValue: function (v) { _pr.v = v; _pr.d = true; }
                        })
                    );
                });
                for (var k = 0; k < 10 && !_pr.d; k++) sleep(100);
                if (_pr.v) {
                    var raw = String(_pr.v);
                    if (raw.charAt(0) === '"') raw = JSON.parse(raw);
                    try {
                        var ids = JSON.parse(raw) || [];
                        if (ids.length > 0) {
                            ui.run(function () {
                                statusTv.setText("已捕获 " + ids.length + "/" + targetCount + " 个视频，可手动点「加入下载」");
                            });
                            addLog("已拦截: " + ids.length + " 个");
                        }
                        if (ids.length >= targetCount) { finishCollect(ids); return; }
                    } catch(e) {}
                }
            }
            // 超时：把已收集的加入队列
            if (!collecting.done) {
                var pr2 = {v: null, d: false};
                var _pr2 = pr2;
                ui.run(function () {
                    wv.evaluateJavascript(_POLL_IDS,
                        new JavaAdapter(android.webkit.ValueCallback, {
                            onReceiveValue: function (v) { _pr2.v = v; _pr2.d = true; }
                        })
                    );
                });
                for (var k = 0; k < 10 && !_pr2.d; k++) sleep(100);
                var finalIds = [];
                try { var r2 = String(_pr2.v||""); if(r2.charAt(0)==='"')r2=JSON.parse(r2); finalIds=JSON.parse(r2)||[]; } catch(e) {}
                addLog("超时，已收集 " + finalIds.length + " 个");
                finishCollect(finalIds);
            }
        });

        // ── 按钮事件 ──
        doneBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
            onClick: function () {
                var pr = {v: null, d: false};
                var _pr = pr;
                wv.evaluateJavascript(_POLL_IDS,
                    new JavaAdapter(android.webkit.ValueCallback, {
                        onReceiveValue: function (v) { _pr.v = v; _pr.d = true; }
                    })
                );
                for (var k = 0; k < 10 && !_pr.d; k++) sleep(100);
                var ids = [];
                try { var r=String(_pr.v||""); if(r.charAt(0)==='"')r=JSON.parse(r); ids=JSON.parse(r)||[]; } catch(e) {}
                finishCollect(ids);
            }
        }));
        closeBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
            onClick: function () { collecting.done = true; closeWin(); }
        }));

    } catch(e) {
        toast("打开采集窗口失败: " + e.message);
        log("openJingxuanCollect error: " + e);
    }
}

// 拉取指定用户作品
function pullUserVideos(profileUrl, maxCount) {
    if (!douyinWv) { toast("请先登录抖音账号"); return; }
    threads.start(function () {
        console.show(); console.clear();
        var secId = parseSecUserId(profileUrl);
        if (!secId) { toast("无法解析用户 ID，请粘贴完整主页链接"); return; }
        addLog("▶ 拉取用户作品 sec_id=" + secId.substring(0, 12) + "…");
        var added = 0, cursor = 0;
        while (added < maxCount) {
            try {
                var batch = Math.min(18, maxCount - added);
                var apiPath2 =
                    "/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web" +
                    "&sec_user_id=" + secId + "&count=" + batch + "&max_cursor=" + cursor +
                    "&locate_query=false&publish_video_strategy_type=2&update_version_code=170400";
                var data;
                try { data = wvNavGet(apiPath2); }
                catch (ne) {
                    addLog("导航式失败: " + ne.message + " → 改用 fetch");
                    data = wvApiGet(apiPath2);
                }
                addLog("用户作品响应 status=" + (data.status_code || "?") +
                       " list=" + ((data.aweme_list || []).length));
                var list = data.aweme_list || [];
                if (!list.length) { addLog("⚠ 列表为空，停止"); break; }
                for (var i = 0; i < list.length && added < maxCount; i++) {
                    var u = awemeToUrl(list[i]);
                    if (u) { enqueueAutoDownload(u); added++; addLog("用户作品 #" + added + " " + shortDesc(list[i])); }
                }
                cursor = data.max_cursor || 0;
                if (!data.has_more) break;
            } catch (e) { addLog("✗ 用户作品: " + e.message); break; }
            sleep(800);
        }
        toast("用户作品已加入队列：" + added + " 个");
    });
}

// 从 aweme 对象构造视频页 URL（交给已有的 getInfoDirect/Fallback 解析）
function awemeToUrl(item) {
    try {
        var id = item.aweme_id || "";
        if (id) return "https://www.douyin.com/video/" + id;
    } catch (e) {}
    return null;
}

// 从主页 URL 提取 sec_user_id
function parseSecUserId(url) {
    // https://www.douyin.com/user/MS4wLjABAAAA...
    var m = url.match(/\/user\/([A-Za-z0-9_\-]{10,})/);
    if (m) return m[1];
    // 兜底：URL 末尾的长字符串
    m = url.match(/([A-Za-z0-9_\-]{20,})/);
    return m ? m[1] : null;
}

function shortDesc(item) {
    return ((item.desc || "").substring(0, 20) || item.aweme_id || "");
}

// ─── 悬浮停止按钮 ─────────────────────────────────────────────────────────────
function showFloatStopBtn() {
    try {
        floatWin = floaty.rawWindow(
            <frame gravity="right|bottom">
                <button id="floatStop" text="⏹ 停止采集"
                        bg="#FF4444" textColor="white" textSize="11sp" padding="12 8 12 8"/>
            </frame>
        );
        floatWin.setSize(-2, -2);
        floatWin.setPosition(0, device.height / 2);
        floatWin.floatStop.on("click", function () { stopAutoCollect(); });
    } catch (e) { log("悬浮窗失败: " + e.message); }
}
function hideFloatStopBtn() {
    if (floatWin) { try { floatWin.close(); } catch (e) {} floatWin = null; }
}

// ─── 后台下载队列 ─────────────────────────────────────────────────────────────
function enqueueAutoDownload(url) {
    dlQueue.push(url);
    if (!dlQueueRunning) runDlQueue();
}
function runDlQueue() {
    if (dlQueueRunning) return;
    dlQueueRunning = true;
    threads.start(function () {
        while (dlQueue.length > 0) {
            // 暂停等待
            while (feedPaused) { sleep(500); }
            var url = dlQueue.shift();
            addDownloadLog("⬇ 解析: " + url.substring(0, 45) + "…");
            try {
                var info = getVideoInfo(url);
                addDownloadLog("⬇ " + info.title.substring(0, 30));
                var fp   = uniquePath(savePath, info.title);
                downloadVideo(info.url, fp, null);
                var sz = (new File(fp).length() / 1048576).toFixed(1);
                addDownloadLog("✓ " + new File(fp).getName() + " (" + sz + " MB)");
                addHistory("✓  " + new File(fp).getName() + "  (" + sz + " MB)", true);
            } catch (e) {
                addDownloadLog("✗ 失败: " + (e.message||"").substring(0, 50));
                addHistory("✗  " + url.substring(0, 40) + "  " + (e.message||"").substring(0,40), false);
            }
        }
        dlQueueRunning = false;
    });
}

// ─── 工具函数 ─────────────────────────────────────────────────────────────────
function uniquePath(dir, title) {
    var fp = dir + "/" + title + ".mp4";
    if (new File(fp).exists()) fp = dir + "/" + title + "_" + Math.floor(Date.now()/1000) + ".mp4";
    return fp;
}
function extractAllUrls(text) {
    var urls = [], seen = {}, re = /https?:\/\/[^\s，。！？、\n\r"'<>]+/g, m;
    while ((m = re.exec(text)) !== null) {
        var u = m[0].replace(/[）)】\]]+$/, "");
        if (!seen[u]) { seen[u] = true; urls.push(u); }
    }
    return urls;
}
function extractUrl(text) {
    var a = extractAllUrls(text);
    if (a.length) return a[0];
    throw new Error("未找到有效的分享链接");
}

// ─── 视频解析 ─────────────────────────────────────────────────────────────────
function resolveVideoId(shareUrl) {
    var cur = shareUrl;
    for (var hop = 0; hop < 8; hop++) {
        var conn = new URL(cur).openConnection();
        conn.setInstanceFollowRedirects(false);
        conn.setRequestProperty("User-Agent", MOBILE_UA);
        conn.setConnectTimeout(10000); conn.setReadTimeout(10000);
        try {
            conn.connect();
            // check current URL first (sometimes the final URL contains the ID)
            var mCur = cur.match(/\/video\/(\d+)/);
            if (mCur) return mCur[1];
            var loc = conn.getHeaderField("Location") || "";
            if (!loc) throw new Error("无法解析视频 ID（重定向链过短）");
            var m = loc.match(/\/video\/(\d+)/);
            if (m) return m[1];
            cur = loc;
        } finally { conn.disconnect(); }
    }
    throw new Error("无法解析视频 ID（超过最大跳转次数）");
}

function getInfoDirect(shareUrl) {
    var videoId = resolveVideoId(shareUrl);
    var resp = http.get("https://www.iesdouyin.com/share/video/" + videoId + "/", {
        headers: { "User-Agent": MOBILE_UA, "Accept": "text/html", "Accept-Language": "zh-CN,zh;q=0.9" }
    });
    var html = resp.body.string();
    var m = html.match(/window\._ROUTER_DATA\s*=\s*(\{[\s\S]+?\})\s*;?\s*<\/script>/);
    if (!m) throw new Error("分享页结构变化");
    var data = JSON.parse(m[1]);
    var vi = deepFind(data, "videoInfoRes");
    if (!vi || !vi.item_list || !vi.item_list.length) throw new Error("视频已删除或私密");
    var item  = vi.item_list[0];
    var title = (item.desc || "").trim() || "抖音视频";
    title = title.replace(/[\\/:*?"<>|#@\n]/g, "_").substring(0, 60);
    return { title: title, url: item.video.play_addr.url_list[0].replace("/playwm/", "/play/") };
}

function getInfoFallback(shareUrl) {
    var resp = http.get(
        "https://douyin.wtf/api/hybrid/video_data?url=" + encodeURIComponent(shareUrl) + "&minimal=false",
        { headers: { "User-Agent": PC_UA } }
    );
    var data = JSON.parse(resp.body.string());
    if (data.code !== 200) throw new Error("备用API: " + (data.message||"未知"));
    var vd = data.data || {}, video = vd.video || {};
    var title = (vd.desc || "").trim() || "抖音视频";
    title = title.replace(/[\\/:*?"<>|#@\n]/g, "_").substring(0, 60);
    var rates = (video.bit_rate||[]).slice().sort(function (a,b) { return (b.bit_rate||0)-(a.bit_rate||0); });
    for (var i = 0; i < rates.length; i++) {
        var list = (rates[i].play_addr||{}).url_list||[];
        for (var j = 0; j < list.length; j++)
            if (list[j].indexOf("douyin.com/aweme/v1/play") !== -1 && list[j].indexOf("dash") === -1)
                return { title: title, url: list[j] };
    }
    throw new Error("备用API未获取到地址");
}

function deepFind(obj, key, depth) {
    if (!depth) depth = 0;
    if (depth > 12 || obj == null) return null;
    if (Array.isArray(obj)) {
        for (var i = 0; i < obj.length; i++) { var r = deepFind(obj[i], key, depth+1); if (r!=null) return r; }
    } else if (typeof obj === "object") {
        if (key in obj) return obj[key];
        for (var k in obj) { var r = deepFind(obj[k], key, depth+1); if (r!=null) return r; }
    }
    return null;
}

function getVideoInfo(text) {
    var url = extractUrl(text), errors = [];
    try { return getInfoDirect(url); }   catch (e) { errors.push("直连: "+(e.message||e)); }
    try { return getInfoFallback(url); } catch (e) { errors.push("备用: "+(e.message||e)); }
    throw new Error(errors.join("\n"));
}

// ─── 流式下载 ────────────────────────────────────────────────────────────────
function downloadVideo(dlUrl, dstPath, onProgress) {
    var conn = new URL(dlUrl).openConnection();
    conn.setRequestProperty("User-Agent", ANDROID_UA);
    conn.setConnectTimeout(60000); conn.setReadTimeout(60000);
    conn.connect();
    var total = conn.getContentLength(), is = conn.getInputStream();
    var dir = new File(dstPath).getParentFile();
    if (!dir.exists()) dir.mkdirs();
    var fos = new FileOutputStream(dstPath);
    var buf = java.lang.reflect.Array.newInstance(java.lang.Byte.TYPE, 512*1024);
    var done = 0, n;
    try {
        while ((n = is.read(buf)) !== -1) {
            fos.write(buf, 0, n); done += n;
            if (onProgress) onProgress(done, total);
        }
        fos.flush();
    } finally { fos.close(); is.close(); conn.disconnect(); }
    return done;
}

// ─── 播放器 ───────────────────────────────────────────────────────────────────

var _pVideos      = [];
var _pIdx         = 0;
var _pMode        = "swipe";
var _pInited      = false;

// UI 引用
var _vv           = null;
var _seekBar      = null;
var _timeTv       = null;
var _titleTv      = null;
var _idxTv        = null;
var _modeBtn      = null;
var _playBtn      = null;
var _swipeRoot    = null;
var _listRoot     = null;
var _listContent  = null;
var _fsBtn        = null;   // 全屏按钮（横屏时可见）

// 状态
var _userPaused   = false;  // 用户主动暂停
var _savedPos     = 0;      // 后台时保存的播放位置
var _wasFocused   = true;   // 上次窗口焦点状态
var _isFullscreen = false;  // 当前是否处于全屏模式
var _swipeLocked  = false;  // 切换动画期间锁住滑动

var _THUMB_COLORS = ["#1E2B3B","#1E3A1E","#2D1E3B","#3B2B1E","#1E3A3A","#3B1E26"];

function initPlayer() {
    if (_pInited) return;
    _pInited = true;

    var ctx  = activity;
    var LL   = android.widget.LinearLayout;
    var FL   = android.widget.FrameLayout;
    var TV   = android.widget.TextView;
    var MATCH = LL.LayoutParams.MATCH_PARENT;
    var WRAP  = LL.LayoutParams.WRAP_CONTENT;
    var root  = ui.pagePlayer;

    root.setOrientation(LL.VERTICAL);
    root.setBackgroundColor(android.graphics.Color.BLACK);

    // ── 顶部栏 ──────────────────────────────────────────────────────────────
    var topBar = new LL(ctx);
    topBar.setOrientation(LL.HORIZONTAL);
    topBar.setGravity(android.view.Gravity.CENTER_VERTICAL);
    topBar.setBackgroundColor(android.graphics.Color.parseColor("#161616"));
    topBar.setPadding(dpToPx(8), 0, dpToPx(8), 0);
    topBar.setLayoutParams(new LL.LayoutParams(MATCH, dpToPx(50)));

    _modeBtn = _pTv(ctx, "≡  列表", 13, "#EEEEEE");
    _modeBtn.setPadding(dpToPx(10), dpToPx(8), dpToPx(10), dpToPx(8));
    _modeBtn.setBackgroundColor(android.graphics.Color.parseColor("#2A2A2A"));
    topBar.addView(_modeBtn);

    _pSpacer(topBar, ctx);

    _idxTv = _pTv(ctx, "— / —", 11, "#666666");
    topBar.addView(_idxTv);

    var refreshTv = _pTv(ctx, "  ↺  ", 20, "#555555");
    refreshTv.setPadding(dpToPx(8), 0, dpToPx(4), 0);
    topBar.addView(refreshTv);

    root.addView(topBar);

    // ── 播放区（FrameLayout 叠加覆盖层）──────────────────────────────────────
    _swipeRoot = new FL(ctx);
    _swipeRoot.setLayoutParams(new LL.LayoutParams(MATCH, 0, 1));
    _swipeRoot.setBackgroundColor(android.graphics.Color.BLACK);

    // VideoView 居中显示（内部会自动保持比例）
    _vv = new android.widget.VideoView(ctx);
    var vvFLP = new FL.LayoutParams(MATCH, MATCH);
    vvFLP.gravity = android.view.Gravity.CENTER;
    _vv.setLayoutParams(vvFLP);
    _swipeRoot.addView(_vv);

    // 顶部标题覆盖
    var topOvr = new LL(ctx);
    topOvr.setOrientation(LL.VERTICAL);
    topOvr.setBackgroundColor(android.graphics.Color.parseColor("#99000000"));
    topOvr.setPadding(dpToPx(16), dpToPx(14), dpToPx(16), dpToPx(14));
    var topOvrLP = new FL.LayoutParams(MATCH, WRAP);
    topOvrLP.gravity = android.view.Gravity.TOP;
    topOvr.setLayoutParams(topOvrLP);

    _titleTv = _pTv(ctx, "", 13, "#FFFFFF");
    _titleTv.setSingleLine(true);
    _titleTv.setEllipsize(android.text.TextUtils.TruncateAt.END);
    topOvr.addView(_titleTv);
    _swipeRoot.addView(topOvr);

    // 底部控制覆盖
    var botOvr = new LL(ctx);
    botOvr.setOrientation(LL.VERTICAL);
    botOvr.setBackgroundColor(android.graphics.Color.parseColor("#CC000000"));
    botOvr.setPadding(dpToPx(16), dpToPx(10), dpToPx(16), dpToPx(18));
    var botOvrLP = new FL.LayoutParams(MATCH, WRAP);
    botOvrLP.gravity = android.view.Gravity.BOTTOM;
    botOvr.setLayoutParams(botOvrLP);

    // 进度条
    _seekBar = new android.widget.SeekBar(ctx);
    _seekBar.setMax(1000);
    _seekBar.setLayoutParams(new LL.LayoutParams(MATCH, WRAP));
    botOvr.addView(_seekBar);

    // 控制行
    var ctrlRow = new LL(ctx);
    ctrlRow.setOrientation(LL.HORIZONTAL);
    ctrlRow.setGravity(android.view.Gravity.CENTER_VERTICAL);
    ctrlRow.setLayoutParams(new LL.LayoutParams(MATCH, dpToPx(44)));

    var prevTv = _pTv(ctx, "⏮", 24, "#DDDDDD");
    prevTv.setPadding(dpToPx(4), 0, dpToPx(12), 0);
    ctrlRow.addView(prevTv);

    _playBtn = _pTv(ctx, "⏸", 28, "#FFFFFF");
    _playBtn.setPadding(dpToPx(4), 0, dpToPx(12), 0);
    ctrlRow.addView(_playBtn);

    var nextTv = _pTv(ctx, "⏭", 24, "#DDDDDD");
    nextTv.setPadding(dpToPx(4), 0, dpToPx(4), 0);
    ctrlRow.addView(nextTv);

    _pSpacer(ctrlRow, ctx);

    _timeTv = _pTv(ctx, "0:00 / 0:00", 11, "#999999");
    ctrlRow.addView(_timeTv);

    _pSpacer(ctrlRow, ctx);

    var delTv = _pTv(ctx, "🗑", 22, "#FF4444");
    delTv.setPadding(dpToPx(4), 0, dpToPx(4), 0);
    ctrlRow.addView(delTv);

    botOvr.addView(ctrlRow);
    _swipeRoot.addView(botOvr);
    root.addView(_swipeRoot);

    // ── 列表区（初始隐藏）────────────────────────────────────────────────────
    _listRoot = new android.widget.ScrollView(ctx);
    _listRoot.setLayoutParams(new LL.LayoutParams(MATCH, 0, 0));
    _listRoot.setBackgroundColor(android.graphics.Color.parseColor("#0F0F0F"));
    _listRoot.setVisibility(android.view.View.GONE);

    _listContent = new LL(ctx);
    _listContent.setOrientation(LL.VERTICAL);
    _listContent.setLayoutParams(new LL.LayoutParams(MATCH, WRAP));
    _listRoot.addView(_listContent);
    root.addView(_listRoot);

    // ── 事件绑定 ────────────────────────────────────────────────────────────

    _modeBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() { _pMode === "swipe" ? _switchToList() : _switchToSwipe(true); }
    }));

    refreshTv.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() { _pRefresh(); }
    }));

    prevTv.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() { _playAt(_pIdx - 1); }
    }));

    nextTv.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() { _playAt(_pIdx + 1); }
    }));

    delTv.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() { _deleteAt(_pIdx, true); }
    }));

    // 播放/暂停按钮（记录用户意图）
    _playBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() {
            if (!_vv) return;
            if (_vv.isPlaying()) {
                _userPaused = true; _vv.pause(); _playBtn.setText("▶");
            } else {
                _userPaused = false; _vv.start(); _playBtn.setText("⏸");
            }
        }
    }));

    _seekBar.setOnSeekBarChangeListener(new JavaAdapter(android.widget.SeekBar.OnSeekBarChangeListener, {
        onProgressChanged: function(sb, prog, fromUser) {
            if (fromUser && _vv) {
                var dur = _vv.getDuration();
                if (dur > 0) _vv.seekTo(Math.round(prog * dur / 1000));
            }
        },
        onStartTrackingTouch: function() {},
        onStopTrackingTouch:  function() {}
    }));

    // ── 丝滑滑动切换（抖音风格）─────────────────────────────────────────────
    var _velTracker  = null;
    var _touchStartY = 0;
    var _dragging    = false;

    _swipeRoot.setOnTouchListener(new JavaAdapter(android.view.View.OnTouchListener, {
        onTouch: function(v, ev) {
            if (_swipeLocked) return true;
            var MA = android.view.MotionEvent;
            var act = ev.getActionMasked();

            if (act === MA.ACTION_DOWN) {
                if (_velTracker) _velTracker.recycle();
                _velTracker  = android.view.VelocityTracker.obtain();
                _velTracker.addMovement(ev);
                _touchStartY = ev.getY();
                _dragging    = false;
                return true;
            }

            if (_velTracker) _velTracker.addMovement(ev);

            if (act === MA.ACTION_MOVE) {
                var dy = ev.getY() - _touchStartY;
                if (Math.abs(dy) > dpToPx(8)) _dragging = true;
                if (_dragging) {
                    // 橡皮筋阻尼：边缘越难拖
                    _swipeRoot.setTranslationY(dy * 0.82);
                }
                return true;
            }

            if (act === MA.ACTION_UP || act === MA.ACTION_CANCEL) {
                var dy = ev.getY() - _touchStartY;
                if (!_dragging || Math.abs(dy) < dpToPx(6)) {
                    // 单击：切换播放/暂停
                    if (_vv) {
                        if (_vv.isPlaying()) { _userPaused = true; _vv.pause(); _playBtn.setText("▶"); }
                        else                 { _userPaused = false; _vv.start(); _playBtn.setText("⏸"); }
                    }
                } else {
                    _velTracker.computeCurrentVelocity(1000);
                    var vy = _velTracker.getYVelocity();
                    var sh = _swipeRoot.getHeight() > 0 ? _swipeRoot.getHeight() : device.height;
                    if (dy < -dpToPx(80) || vy < -700) {
                        _doSwipe(1, sh);   // 上划 → 下一个
                    } else if (dy > dpToPx(80) || vy > 700) {
                        _doSwipe(-1, sh);  // 下划 → 上一个
                    } else {
                        // 回弹
                        _swipeRoot.animate().translationY(0).setDuration(220)
                            .setInterpolator(new android.view.animation.DecelerateInterpolator(1.5))
                            .start();
                    }
                }
                if (_velTracker) { _velTracker.recycle(); _velTracker = null; }
                return true;
            }
            return false;
        }
    }));

    // ── 横屏全屏按钮 ─────────────────────────────────────────────────────────
    _fsBtn = _pTv(ctx, "⛶", 22, "#FFFFFFBB");
    _fsBtn.setBackgroundColor(android.graphics.Color.parseColor("#55000000"));
    _fsBtn.setPadding(dpToPx(12), dpToPx(8), dpToPx(12), dpToPx(8));
    var fsBLP = new FL.LayoutParams(WRAP, WRAP);
    fsBLP.gravity = android.view.Gravity.TOP | android.view.Gravity.RIGHT;
    fsBLP.topMargin = dpToPx(14); fsBLP.rightMargin = dpToPx(14);
    _fsBtn.setLayoutParams(fsBLP);
    _fsBtn.setVisibility(android.view.View.GONE);
    _fsBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
        onClick: function() { _isFullscreen ? _exitFullscreen() : _enterFullscreen(); }
    }));
    _swipeRoot.addView(_fsBtn);

    // 方向变化监听（横/竖屏切换时显隐全屏按钮）
    ui.pagePlayer.getViewTreeObserver().addOnGlobalLayoutListener(
        new JavaAdapter(android.view.ViewTreeObserver.OnGlobalLayoutListener, {
            onGlobalLayout: function() {
                if (!_pInited || !_fsBtn) return;
                var w = ui.pagePlayer.getWidth();
                var h = ui.pagePlayer.getHeight();
                if (w > 0 && h > 0) {
                    var landscape = w > h;
                    _fsBtn.setVisibility(landscape ? android.view.View.VISIBLE : android.view.View.GONE);
                    if (!landscape && _isFullscreen) _exitFullscreen();
                }
            }
        }));

    // ── VideoView 事件 ───────────────────────────────────────────────────────
    _vv.setOnCompletionListener(new JavaAdapter(android.media.MediaPlayer.OnCompletionListener, {
        onCompletion: function() { _userPaused = false; _playAt(_pIdx + 1); }
    }));
    _vv.setOnErrorListener(new JavaAdapter(android.media.MediaPlayer.OnErrorListener, {
        onError: function(mp, what, extra) {
            if (_titleTv) _titleTv.setText("⚠ 播放失败，尝试下一个");
            _playAt(_pIdx + 1);
            return true;
        }
    }));

    // ── 黑屏修复：窗口焦点变化时保存位置并在回来时恢复 ────────────────────
    activity.getWindow().getDecorView().getViewTreeObserver()
        .addOnWindowFocusChangeListener(
            new JavaAdapter(android.view.ViewTreeObserver.OnWindowFocusChangeListener, {
                onWindowFocusChanged: function(hasFocus) {
                    if (!_pInited || _currentTab !== "player" || !_vv || _pVideos.length === 0) {
                        _wasFocused = hasFocus; return;
                    }
                    if (!hasFocus) {
                        // 记录位置
                        try { _savedPos = _vv.getCurrentPosition(); } catch(e) { _savedPos = 0; }
                    } else if (!_wasFocused && !_userPaused) {
                        // 从后台回来：重新加载并定位
                        var f  = _pVideos[_pIdx];
                        var ps = _savedPos;
                        try {
                            _vv.setVideoPath(f.getAbsolutePath());
                            _vv.seekTo(ps > 0 ? ps : 0);
                            _vv.start();
                            if (_playBtn) _playBtn.setText("⏸");
                        } catch(e) {}
                    }
                    _wasFocused = hasFocus;
                }
            }));

    // 进度更新循环
    _startProgressLoop();

    // 扫描并播放
    threads.start(function() {
        _pVideos = _scanVideos(savePath);
        ui.run(function() {
            if (_pVideos.length > 0) {
                _playAt(0);
            } else {
                if (_titleTv) _titleTv.setText("📂 " + savePath + " 中暂无视频");
                if (_idxTv)   _idxTv.setText("0 / 0");
            }
        });
    });
}

// ── 抖音风格滑动动画 ──────────────────────────────────────────────────────────
function _doSwipe(dir, sh) {
    _swipeLocked = true;
    var exitY  = dir > 0 ? -sh : sh;  // 当前视频退出方向
    var enterY = -exitY;               // 新视频进入方向

    _swipeRoot.animate()
        .translationY(exitY)
        .setDuration(260)
        .setInterpolator(new android.view.animation.AccelerateInterpolator(1.3))
        .withEndAction(new JavaAdapter(java.lang.Runnable, {
            run: function() {
                _playAt(_pIdx + dir);
                _swipeRoot.setTranslationY(enterY);
                _swipeRoot.animate()
                    .translationY(0)
                    .setDuration(230)
                    .setInterpolator(new android.view.animation.DecelerateInterpolator(1.3))
                    .withEndAction(new JavaAdapter(java.lang.Runnable, {
                        run: function() { _swipeLocked = false; }
                    }))
                    .start();
            }
        }))
        .start();
}

// ── 全屏模式 ──────────────────────────────────────────────────────────────────
function _enterFullscreen() {
    _isFullscreen = true;
    if (_fsBtn) _fsBtn.setText("✕  退出");
    activity.getWindow().getDecorView().setSystemUiVisibility(
        android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
        android.view.View.SYSTEM_UI_FLAG_FULLSCREEN |
        android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
        android.view.View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
        android.view.View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
        android.view.View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
    ui.appTabDivider.setVisibility(View.GONE);
    ui.appTabBar.setVisibility(View.GONE);
}

function _exitFullscreen() {
    _isFullscreen = false;
    if (_fsBtn) _fsBtn.setText("⛶");
    activity.getWindow().getDecorView().setSystemUiVisibility(
        android.view.View.SYSTEM_UI_FLAG_VISIBLE);
    ui.appTabDivider.setVisibility(View.VISIBLE);
    ui.appTabBar.setVisibility(View.VISIBLE);
}

// ── 辅助：创建可点击 TextView ─────────────────────────────────────────────────
function _pTv(ctx, text, spSize, hexColor) {
    var tv = new android.widget.TextView(ctx);
    tv.setText(text);
    tv.setTextColor(android.graphics.Color.parseColor(hexColor));
    tv.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, spSize);
    tv.setClickable(true);
    return tv;
}
function _pSpacer(parent, ctx) {
    var sp = new android.view.View(ctx);
    sp.setLayoutParams(new android.widget.LinearLayout.LayoutParams(0, 1, 1));
    parent.addView(sp);
}

// ── 扫描视频文件 ──────────────────────────────────────────────────────────────
function _scanVideos(dir) {
    var EXT = [".mp4", ".mov", ".mkv", ".avi", ".flv", ".webm", ".m4v"];
    var files = new File(dir).listFiles() || [];
    var videos = [];
    for (var i = 0; i < files.length; i++) {
        var n = String(files[i].getName()).toLowerCase();
        for (var j = 0; j < EXT.length; j++) {
            if (n.lastIndexOf(EXT[j]) === n.length - EXT[j].length) {
                videos.push(files[i]); break;
            }
        }
    }
    videos.sort(function(a, b) { return b.lastModified() - a.lastModified(); });
    return videos;
}

// ── 播放指定下标的视频 ────────────────────────────────────────────────────────
function _playAt(idx) {
    if (_pVideos.length === 0) return;
    _pIdx = ((idx % _pVideos.length) + _pVideos.length) % _pVideos.length;
    var f = _pVideos[_pIdx];
    try {
        _vv.setVideoPath(f.getAbsolutePath());
        _vv.start();
        _playBtn.setText("⏸");
        _titleTv.setText(String(f.getName()).replace(/\.[^.]+$/, ""));
        _idxTv.setText((_pIdx + 1) + " / " + _pVideos.length);
    } catch(e) { addLog("播放错误: " + e.message); }
}

// ── 进度条更新循环（绑定在 VideoView 的 postDelayed 上）─────────────────────
function _startProgressLoop() {
    var ticker = new JavaAdapter(java.lang.Runnable, {
        run: function() {
            try {
                if (_vv && _seekBar && _timeTv && _pMode === "swipe") {
                    var cur = _vv.getCurrentPosition();
                    var dur = _vv.getDuration();
                    if (dur > 0) {
                        _seekBar.setProgress(Math.round(cur * 1000 / dur));
                        _timeTv.setText(_fmtMs(cur) + " / " + _fmtMs(dur));
                    }
                }
            } catch(e) {}
            if (_vv && _pInited) _vv.postDelayed(ticker, 500);
        }
    });
    _vv.postDelayed(ticker, 500);
}

function _fmtMs(ms) {
    var s = Math.floor(ms / 1000), m = Math.floor(s / 60);
    s = s % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
}

// ── 模式切换 ──────────────────────────────────────────────────────────────────
function _switchToList() {
    _pMode = "list";
    _modeBtn.setText("▶  播放器");
    var MATCH = android.widget.LinearLayout.LayoutParams.MATCH_PARENT;
    _swipeRoot.setLayoutParams(new android.widget.LinearLayout.LayoutParams(MATCH, 0, 0));
    _swipeRoot.setVisibility(android.view.View.GONE);
    _listRoot.setLayoutParams(new android.widget.LinearLayout.LayoutParams(MATCH, 0, 1));
    _listRoot.setVisibility(android.view.View.VISIBLE);
    if (_vv && _vv.isPlaying()) _vv.pause();
    _buildList();
}

function _switchToSwipe(resume) {
    _pMode = "swipe";
    _modeBtn.setText("≡  列表");
    var MATCH = android.widget.LinearLayout.LayoutParams.MATCH_PARENT;
    _swipeRoot.setLayoutParams(new android.widget.LinearLayout.LayoutParams(MATCH, 0, 1));
    _swipeRoot.setVisibility(android.view.View.VISIBLE);
    _listRoot.setLayoutParams(new android.widget.LinearLayout.LayoutParams(MATCH, 0, 0));
    _listRoot.setVisibility(android.view.View.GONE);
    // resume=true：从暂停态恢复；false/undefined：由调用方负责 playAt
    if (resume === true && _pVideos.length > 0 && _vv && !_vv.isPlaying()) {
        _userPaused = false; _vv.start();
    }
    if (_playBtn) _playBtn.setText(_vv && _vv.isPlaying() ? "⏸" : "▶");
}

// ── 构建列表 ──────────────────────────────────────────────────────────────────
function _buildList() {
    _listContent.removeAllViews();
    var ctx   = activity;
    var LL    = android.widget.LinearLayout;
    var FL    = android.widget.FrameLayout;
    var TV    = android.widget.TextView;
    var MATCH = LL.LayoutParams.MATCH_PARENT;
    var WRAP  = LL.LayoutParams.WRAP_CONTENT;

    if (_pVideos.length === 0) {
        var emTv = _pTv(ctx, "暂无视频\n保存目录：" + savePath, 13, "#555555");
        emTv.setGravity(android.view.Gravity.CENTER);
        emTv.setPadding(dpToPx(24), dpToPx(80), dpToPx(24), dpToPx(24));
        _listContent.addView(emTv);
        return;
    }

    // 顶部统计行
    var statRow = new LL(ctx);
    statRow.setOrientation(LL.HORIZONTAL);
    statRow.setGravity(android.view.Gravity.CENTER_VERTICAL);
    statRow.setPadding(dpToPx(16), dpToPx(12), dpToPx(16), dpToPx(12));
    statRow.setLayoutParams(new LL.LayoutParams(MATCH, WRAP));

    var statTv = _pTv(ctx, "共 " + _pVideos.length + " 个视频", 12, "#888888");
    statRow.addView(statTv);
    _listContent.addView(statRow);

    // 分隔线
    var div = new android.view.View(ctx);
    div.setBackgroundColor(android.graphics.Color.parseColor("#222222"));
    div.setLayoutParams(new LL.LayoutParams(MATCH, 1));
    _listContent.addView(div);

    for (var i = 0; i < _pVideos.length; i++) {
        (function(idx, file) {
            var row = new LL(ctx);
            row.setOrientation(LL.HORIZONTAL);
            row.setGravity(android.view.Gravity.CENTER_VERTICAL);
            row.setBackgroundColor(android.graphics.Color.parseColor(
                idx === _pIdx ? "#1E2D1E" : "#141414"));
            row.setPadding(dpToPx(14), dpToPx(12), dpToPx(10), dpToPx(12));
            var rowLP = new LL.LayoutParams(MATCH, WRAP);
            rowLP.bottomMargin = dpToPx(1);
            row.setLayoutParams(rowLP);

            // 缩略图占位（带序号）
            var thumb = new FL(ctx);
            thumb.setBackgroundColor(android.graphics.Color.parseColor(
                _THUMB_COLORS[idx % _THUMB_COLORS.length]));
            thumb.setLayoutParams(new LL.LayoutParams(dpToPx(60), dpToPx(44)));

            var thumbIcon = _pTv(ctx, idx === _pIdx ? "▶" : "" + (idx + 1), 14,
                idx === _pIdx ? "#FFFFFF" : "#FFFFFF88");
            thumbIcon.setGravity(android.view.Gravity.CENTER);
            var thumbLP = new FL.LayoutParams(
                FL.LayoutParams.MATCH_PARENT, FL.LayoutParams.MATCH_PARENT);
            thumbLP.gravity = android.view.Gravity.CENTER;
            thumbIcon.setLayoutParams(thumbLP);
            thumb.addView(thumbIcon);
            row.addView(thumb);

            // 文件信息
            var info = new LL(ctx);
            info.setOrientation(LL.VERTICAL);
            info.setLayoutParams(new LL.LayoutParams(0, WRAP, 1));
            info.setPadding(dpToPx(12), 0, dpToPx(8), 0);

            var nameTv = _pTv(ctx, String(file.getName()).replace(/\.[^.]+$/, ""), 12,
                idx === _pIdx ? "#FFFFFF" : "#DDDDDD");
            nameTv.setSingleLine(true);
            nameTv.setEllipsize(android.text.TextUtils.TruncateAt.END);
            info.addView(nameTv);

            var sizeTv = _pTv(ctx, (file.length() / 1048576).toFixed(1) + " MB", 10, "#555555");
            sizeTv.setPadding(0, dpToPx(3), 0, 0);
            info.addView(sizeTv);

            row.addView(info);

            // 删除按钮
            var delBtn = _pTv(ctx, "✕", 16, "#FF4444");
            delBtn.setPadding(dpToPx(12), dpToPx(6), dpToPx(6), dpToPx(6));
            row.addView(delBtn);

            // 点击行：切回播放器模式，播放该视频
            row.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
                onClick: function() {
                    _pIdx = idx;
                    _switchToSwipe(false);  // 不自动 start，由 _playAt 接管
                    _userPaused = false;
                    _playAt(idx);
                }
            }));

            delBtn.setOnClickListener(new JavaAdapter(android.view.View.OnClickListener, {
                onClick: function() { _deleteAt(idx, false); }
            }));

            _listContent.addView(row);
        })(i, _pVideos[i]);
    }

    // 异步加载每个视频的时长（快速操作，每个约几毫秒）
    threads.start(function() {
        for (var i = 0; i < _pVideos.length; i++) {
            try {
                var mmr = new android.media.MediaMetadataRetriever();
                mmr.setDataSource(_pVideos[i].getAbsolutePath());
                var durStr = mmr.extractMetadata(
                    android.media.MediaMetadataRetriever.METADATA_KEY_DURATION);
                mmr.release();
                var durMs = parseInt(durStr) || 0;
                if (durMs > 0) {
                    // 找到对应 row 的 sizeTv 并更新（通过下标定位子 View）
                    // index +2 because statRow + divider above
                    (function(rowIdx, dur) {
                        ui.run(function() {
                            try {
                                var row = _listContent.getChildAt(rowIdx + 2);
                                if (row instanceof android.widget.LinearLayout) {
                                    var infoLL = row.getChildAt(1);
                                    if (infoLL instanceof android.widget.LinearLayout) {
                                        var sz = infoLL.getChildAt(1);
                                        if (sz instanceof android.widget.TextView) {
                                            sz.setText((_pVideos[rowIdx].length() / 1048576).toFixed(1)
                                                + " MB  ·  " + _fmtMs(dur));
                                        }
                                    }
                                }
                            } catch(e2) {}
                        });
                    })(i, durMs);
                }
            } catch(e) {}
        }
    });
}

// ── 删除视频 ──────────────────────────────────────────────────────────────────
function _deleteAt(idx, fromSwipe) {
    if (idx < 0 || idx >= _pVideos.length) return;
    var f = _pVideos[idx];
    threads.start(function() {
        var ok = dialogs.confirm("删除视频",
            "确定删除「" + String(f.getName()) + "」？\n此操作不可恢复");
        if (!ok) return;
        try {
            if (_vv && _pIdx === idx) _vv.stopPlayback();
            f.delete();
            _pVideos.splice(idx, 1);
            if (_pIdx >= _pVideos.length && _pIdx > 0) _pIdx--;
            toast("已删除");
            ui.run(function() {
                if (_pVideos.length === 0) {
                    if (_titleTv) _titleTv.setText("暂无视频");
                    if (_idxTv)   _idxTv.setText("0 / 0");
                    if (_seekBar) _seekBar.setProgress(0);
                    if (_timeTv)  _timeTv.setText("0:00 / 0:00");
                } else {
                    if (fromSwipe) _playAt(_pIdx);
                    else           _buildList();   // 列表模式：重建列表（只调一次）
                }
            });
        } catch(e) { toast("删除失败：" + e.message); }
    });
}

// ── 刷新视频列表 ──────────────────────────────────────────────────────────────
function _pRefresh() {
    threads.start(function() {
        _pVideos = _scanVideos(savePath);
        ui.run(function() {
            if (_idxTv) _idxTv.setText((_pVideos.length > 0 ? _pIdx + 1 : 0) + " / " + _pVideos.length);
            if (_pMode === "list") _buildList();
            toast("已刷新，共 " + _pVideos.length + " 个视频");
        });
    });
}
