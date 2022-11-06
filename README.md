# sgcc_electricity

本应用可以帮助你将国网的电费、用电量数据接入HA，适用于除南方电网覆盖省份外的用户。即除广东、广西、云南、贵州、海南等省份的用户外，均可使用本应用获取电力、电费数据。

本应用在启动后和每天早上8点抓取数据，并在HA里更新sensor.last_electricity_usage（最近一天用电量）与sensor.electricity_charge_balance（电费余额）。

由于采用REST API方式创建sensor，没有做实体注册，无法在webui里编辑。如果需要，你可以在configuration.yaml下增加如下配置后重启HA，这样你就可在webUI编辑对应的实体了。

```yaml
template:
  - trigger:
      - platform: event
        event_type: "state_changed"
        event_data: 
          entity_id: sensor.electricity_charge_balance
    sensor:
      - name: electricity_charge_balance_entity
        unique_id: electricity_charge_balance_entity
        state: "{{ states('sensor.electricity_charge_balance') }}"
        state_class: measurement
        unit_of_measurement: "CNY"
 
  - trigger:
      - platform: event
        event_type: "state_changed"
        event_data: 
          entity_id: sensor.last_electricity_usage
    sensor:
      - name: last_electricity_usage_entity
        unique_id: last_electricity_usage_entity
        state: "{{ states('sensor.last_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "KWH"
```

## 使用方法一：直接作为add-on接入

__如果你是采用supervised, HAOS方式部署的home-assistant（也就是说你部署了suppervisor, add-on等容器），可以使用local add-on的方式接入.__

首先，进入HA实例终端，输入以下命令从git上clone仓库。

```bash
cd /addons
git clone https://github.com/louisslee/sgcc_electricity.git
cd sgcc_electricity
chmod 777 run.sh
```

然后在webUI上点击配置-》加载项-》加载项商店，这时你应该可以看到local下面的本add-on（没看到的话，加载项商店又上角点击检查更新，再不行你可以试试重启supervisor）。

由于这个项目较大（docker image约1.17GB），build过程较慢，预计持续半小时左右（视网速、科学情况有所差异），先喝杯奶茶休息下再回来吧：）

如果你想了解setup进度，可以在HA终端上输入docker container ls，复制第一个container的name，执行docker container attach {替换成container name},来查看安装进度。

安装好后，配置好用户名、密码，直接启动即可。稍等1分钟后，就可以在HA中找到sensor.last_electricity_usage与sensor.electricity_charge_balance这两个实体了。


## 使用方法二：docker部署

__如果你是采用core, docker方式部署的home-assistant（也就是说你没有部署suppervisor, add-on等容器），建议采用docker部署本应用。__

首先请在HA webUI上建立一个长期访问令牌，点击webUI左下角用户名拉到最下面就可以看到了。

在宿主机上打开压缩包后，可输入如下命令执行docker构建、部署。

```bash
git clone https://github.com/louisslee/sgcc_electricity.git
cd sgcc_electricity
chmod 777 run.sh
docker build -t sgcc_electricity:1.0 .
docker run --name sgcc_electricity -d -e PHONE_NUMBER="" -e PASSWORD="" -e HASS_URL="" -e HASS_TOKEN="" --restart unless-stopped sgcc/electricity:1.0 
```
由于这个项目较大（docker image约1.17GB），build过程较慢，我在ubuntu上build了十多分钟。

部署container成功后稍等1分钟，你就可以在HA中找到sensor.last_electricity_usage与sensor.electricity_charge_balance这两个实体了。

## 使用方法三：直接部署

__如果你宿主机是ubuntu，centos, debian等linux操作系统，底层C库是glibc等manylinux tag可兼容的，你可以直接在宿主机上部署本应用（如果底层C库是musl（如alpine OS）, 需要先自行编译onnxruntime）__

首先安装本项目依赖，可参考：

```bash
pip3 install selenium==4.5.0, schedule==1.1.0, ddddocr==1.4.7, undetected_webdriver==3.1.6
apt-get install jq chromium=90.0.4430.212-1~deb10u1 -y #chromium版本如果没有，可以选用系统上有的，并在const.py上修改chrom的版本，由90改成你安装的大版本。
```

将文件解压后，执行python脚本即可。可根据需求自行将其设置为开机自启动或是跟随HA自启动。

```shell
cd sgcc_electricity
nohup python3 main.py --PHONE_NUMBER= --PASSWORD= --HASS_URL= --HASS_TOKEN= &
```

## 其他

如果你是以core的方式部署的HA，你还可以自己改改，搞一个自定义集成。

