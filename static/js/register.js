$(function() {
    function BindCaptchaBtnClick() {
        $("#captcha-btn").click(function() {
            let $this = $(this); // 保存按钮 jQuery 对象（避免重复查找 DOM）
            let email = $("input[name='email']").val().trim(); // 加 trim() 去除首尾空格

            // 1. 验证邮箱格式（优化：仅判断非空不够，简单校验格式）
            if (!email) {
                alert("请先输入邮箱！");
                return;
            }
            if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                alert("请输入有效的邮箱格式！");
                return;
            }

            // 2. 取消当前点击事件，避免重复点击
            $this.off("click").prop("disabled", true); // 加 disabled 属性，视觉上禁用按钮

                        // 4. （可选）调用后端接口发送验证码（实际项目需添加）
            $.ajax({
             url: "/auth/captcha/?email="+email, // 后端接口地址
             type: "GET",
             success: function(res) {
                 if (res.code !== 200) {
                     alert("验证码发送失败：" + res.msg);
                     // 发送失败时，立即恢复按钮状态
                     clearInterval(timer);
                     $this.text("获取验证码").prop("disabled", false);
                     BindCaptchaBtnClick();
                 }else{
                      console.log(res);
                      $("input[name='captcha']").val(res.message);
//                    alert("验证码发送成功：" + res.message);
                 }
             },
             error: function() {
                 alert("网络错误，验证码发送失败！");
                 clearInterval(timer);
                 $this.text("获取验证码").prop("disabled", false);
                 BindCaptchaBtnClick();
             }
            });

            // 3. 倒计时逻辑
            let countdown = 60; // 推荐设为 60s（更符合实际场景）
            const timer = setInterval(function() {
                if (countdown <= 0) {
                    // 倒计时结束：恢复按钮状态
                    $this.text("获取验证码").prop("disabled", false);
                    clearInterval(timer);
                    BindCaptchaBtnClick(); // 重新绑定点击事件
                } else {
                    countdown--; // 修复：英文分号
                    $this.text(countdown + "s 后重新获取"); // 优化文案，更清晰
                }
            }, 1000);
        });
    }

    // 初始化绑定点击事件
    BindCaptchaBtnClick();
});