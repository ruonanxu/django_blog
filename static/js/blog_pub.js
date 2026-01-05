/* html是从上往下加载的，若不加这句，把 <script> 写在header中 会导致下面引用的元素 加载失败 */
window.onload = function() {
    // 🌟 关键优化1：校验依赖（避免未加载jQuery/wangEditor导致的报错）
    if (typeof jQuery === 'undefined') {
        alert("错误：jQuery 未加载，请检查引入顺序！");
        return;
    }
    if (typeof window.wangEditor === 'undefined') {
        alert("错误：富文本编辑器 wangEditor 未加载！");
        return;
    }

    // 🌟 关键优化2：编辑器初始化容错（避免DOM不存在导致的崩溃）
    let editor = null;
    let toolbar = null;
    const { createEditor, createToolbar } = window.wangEditor;

    try {
        // 编辑器配置（优化提示文案，更贴合中文场景）
        const editorConfig = {
            placeholder: '请输入博客内容（支持富文本格式）...',
            onChange(editor) {
                const html = editor.getHtml();
                console.log('编辑器实时内容：', html);
                // 可选：同步到隐藏textarea（用于表单备份，可选）
                // $("textarea[name='content-backup']").val(html);
            },
        };

        // 初始化编辑器（确保DOM元素存在）
        editor = createEditor({
            selector: '#editor-container',
            html: '<p><br></p>',
            config: editorConfig,
            mode: 'default',
        });

        // 初始化工具栏
        const toolbarConfig = {};
        toolbar = createToolbar({
            editor,
            selector: '#toolbar-container',
            config: toolbarConfig,
            mode: 'default',
        });
    } catch (e) {
        console.error("富文本编辑器初始化失败：", e);
        alert("编辑器加载失败，请刷新页面重试（检查容器元素是否存在）！");
        return;
    }

    // 🌟 关键优化3：发布按钮点击事件（完善验证+用户体验）
    $('#submit-btn').click(function(event) {
        event.preventDefault(); // 阻止表单默认提交（核心：避免页面刷新）

        // 1. 获取表单数据（trim() 去除首尾空格）
        const title = $("input[name='title']").val().trim();
        const category = $("#category").val().trim();
        const csrfmiddlewaretoken = $("input[name='csrfmiddlewaretoken']").val().trim();
        const content = editor.getHtml().trim();

        // 2. 前端严格验证（减少无效请求，提升体验）
        if (!title) {
            alert("请输入博客标题！");
            $("input[name='title']").focus(); // 聚焦到标题输入框
            return;
        }
        if (!category) {
            alert("请选择博客分类！");
            $("#category").focus(); // 聚焦到分类选择器
            return;
        }
        if (!csrfmiddlewaretoken) {
            alert("错误：CSRF令牌缺失，无法提交（请检查模板是否添加 {% csrf_token %}）！");
            return;
        }
        // 排除空富文本（仅换行/空格的无效内容）
        if (!content || content === '<p><br></p>' || content === '<br>' || content === '') {
            alert("请输入博客内容，不能为空！");
            editor.focus(); // 聚焦到编辑器
            return;
        }

        // 🌟 关键优化4：防止重复提交（禁用按钮+加载提示）
        const $btn = $(this);
        $btn.text("发布中...").prop("disabled", true);

        // 3. AJAX 异步提交（优化配置，增强稳定性）
        $.ajax({
            url: "/blog/public/",
            method: "POST",
            data: {
                title: title,
                category: category,
                csrfmiddlewaretoken: csrfmiddlewaretoken,
                content: content // 富文本HTML内容（后端需用TextField存储）
            },
            dataType: "json", // 明确指定后端返回JSON格式
            timeout: 10000, // 超时时间：10秒（避免无限等待）
            success: function(res) {
                if (res.code !== 200) {
                    alert("发布失败：" + (res.message || "未知错误"));
                } else {
                    alert("发布成功！" + (res.message || "即将跳转至博客列表"));
                    // 可选：发布成功后跳转（推荐）
                    setTimeout(() => {
                        window.location.href = "/blog/index/"; // 跳转到博客列表页
                    }, 1500); // 1.5秒后跳转，给用户看提示
                    // 若不跳转，清空表单：
                    // $("input[name='title']").val("");
                    // $("#category").val("");
                    // editor.setHtml("<p><br></p>");
                }
            },
            error: function(xhr, status, error) {
                // 详细错误日志（方便调试）
                console.error("AJAX请求失败：");
                console.error("状态码：", xhr.status);
                console.error("错误类型：", status);
                console.error("后端响应：", xhr.responseText);
                // 用户友好提示
                if (status === "timeout") {
                    alert("发布超时，请检查网络后重试！");
                } else {
                    alert("网络错误或服务器异常，发布失败！");
                }
            },
            complete: function() {
                // 🌟 关键优化5：请求完成后恢复按钮状态（无论成功/失败）
                $btn.text("发布博客").prop("disabled", false);
            }
        });
    });
};