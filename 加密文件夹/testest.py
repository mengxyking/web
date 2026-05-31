import uiautomator2 as u2

d = u2.connect("ALTMVB3B17005679")

print(d.app_current()["package"])
print(d.dump_hierarchy())
if (not d(resourceId="com.huanyou.fjxasn:id/txt_top_center").exists(timeout=3)):
    print("当前不在会话页面，请移步到会话页面")
    #continue



#print(d.dump_hierarchy())