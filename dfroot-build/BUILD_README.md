# DirtyFrag dfroot.ko 自定义构建（iQOO Neo8 / 内核 5.10.246）

用途：为 iQOO Neo8 的 **OriginOS 6 / 内核 5.10.246-gki-gb142569a7856** 编译一个匹配的
`dfroot.ko`（DirtyFrag / DFRoot 的内核模块），解决"官方只提供 5.10.245 / 5.10.252 的 ko"问题。

## 原理
- DirtyFrag 的 `libdfroot.so` 内嵌 8 个 ko，**按内核 vermagic 精确匹配**
- 你的内核 vermagic 是 `5.10.246-gki-gb142569a7856 SMP preempt mod_unload modversions aarch64`
- 官方没编这个版本 → 用 `lkm/dfroot.c` 源码 + **Google DDK（android12-5.10）** 自己编一个
- 编译用官方 CI 同款镜像 `ghcr.io/ylarod/ddk-min:android12-5.10-20260828`
  （它带 `Module.symvers`，保证符号 CRC 与同 KMI 内核兼容）
- 编完由 `patch_vermagic.py` 把 `.modinfo` 的 vermagic 精确改成你的版本

## 使用步骤
1. 在 GitHub 上新建一个仓库（public / private 都行，随便起名）
2. 把本目录**全部内容**传上去（注意 `.github/workflows/build.yml` 也要传，别漏了隐藏目录）
   - 网页上传：Add file -> Upload files -> 把本目录文件全拖进去
   - 或命令行：
     ```
     git init
     git add .
     git commit -m "build dfroot for 5.10.246"
     git branch -M main
     git remote add origin <你的仓库地址>
     git push -u origin main
     ```
3. 打开仓库的 **Actions** 标签 -> 左侧 `Build dfroot.ko (iQOO Neo8 / android12-5.10)`
   -> 点 **Run workflow**（如果在 push 后自动跑起来了，就不用点）
4. 等 2~5 分钟，跑完后在该次运行的页面底部 **Artifacts** 里下载
   `dfroot-android12-5.10-246.zip`，里面就是 `dfroot.ko`
5. 想换别的内核版本：改 `build.yml` 里的 `TARGET_VERMAGIC` 环境变量，重跑一次即可

## 产物怎么用
拿到的 `dfroot.ko` 有两条路放进 DirtyFrag：

- **路 A（推荐，免重编 App）**：用同样的方法把 ko 塞回 APK 的
  `lib/arm64-v8a/libdfroot.so`（替换对应 KMI 的内嵌 ko），重签 APK
- **路 B**：让 App 用外部 ko（需要改 App 逻辑）

## 日志自查
编译步骤里会打印：
```
--- built vermagic ---           <- DDK 编出来的原始值（应该是 5.10.252-dirty）
--- final vermagic ---           <- patch 之后（应该是 5.10.246-gki-gb142569a7856 ...）
```
两次都看清楚再下载。

## 注意
- 只在你**自己拥有/获授权**的设备上使用
- 这是**临时 root**（重启失效），不刷机、不解锁 bootloader
- 若加载时报 `disagrees about version of symbol` / `unknown symbol`，说明符号 CRC 或导出有问题，
  需要改用你内核自己的 `Module.symvers` 重编（比 DDK 的更精确）
