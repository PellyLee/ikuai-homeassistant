# Phase 4 组件 schema 详解

## APConfigUpdate
required: id, tagname, comment, gid, mlo_radio0, mlo_radio1, mlo_radio2, flicker, lights, ssid1, ssid2, hide_ssid1, hide_ssid2, isolate1, isolate2, qos_atf, load_strategy, autohide_maxsta, autohide_resume, max_pc, channel, min_signal, enc1, key1, enc2, key2, ssid1_vlan, ssid1_vlan_id, ssid2_vlan, ssid2_vlan_id, ssid1_ratelimit, ssid1_upload, ssid1_download, ssid2_ratelimit, ssid2_upload, ssid2_download, auth_server1, auth_port1, acct_secret1, slave_auth1, slave_auth_server1, slave_auth_port1, slave_acct_secret1, auth_server2, auth_port2, acct_secret2, slave_auth2, slave_auth_server2, slave_auth_port2, slave_acct_secret2, signal_str, studio_ssid, ssid3, ssid4, hide_ssid3, hide_ssid4, isolate3, isolate4, qos_atf_5g, load_strategy_5g, autohide_maxsta_5g, autohide_resume_5g, max_pc_5g, channel_5g, min_signal_5g, enc3, key3, enc4, key4, ssid3_vlan, ssid3_vlan_id, ssid4_vlan, ssid4_vlan_id, ssid3_ratelimit, ssid3_upload, ssid3_download, ssid4_ratelimit, ssid4_upload, ssid4_download, auth_server3, auth_port3, acct_secret3, slave_auth3, slave_auth_server3, slave_auth_port3, slave_acct_secret3, auth_server4, auth_port4, acct_secret4, slave_auth4, slave_auth_server4, slave_auth_port4, slave_acct_secret4, signal_str_5g, studio_ssid_5g, task_switch1, task_strategy1, task_date1, task_time1, task_switch2, task_strategy2, task_date2, task_time2, task_switch3, task_strategy3, task_date3, task_time3, reboot_strategy, reboot_date, channel_width_2g, channel_width_5g, port1_vlan, port1_vlan_id, port2_vlan, port2_vlan_id, port3_vlan, port3_vlan_id, port4_vlan, port4_vlan_id, ap_roaming, perfer_5g, studio_mode, gateway_check, country, ssid_union, ssid5, ssid6, hide_ssid5, hide_ssid6, isolate5, isolate6, enc5, key5, enc6, key6, ssid5_vlan, ssid5_vlan_id, ssid6_vlan, ssid6_vlan_id, ssid5_ratelimit, ssid5_upload, ssid5_download, ssid6_ratelimit, ssid6_upload, ssid6_download, auth_server5, auth_port5, acct_secret5, slave_auth5, slave_auth_server5, slave_auth_port5, slave_acct_secret5, auth_server6, auth_port6, acct_secret6, slave_auth6, slave_auth_server6, slave_auth_port6, slave_acct_secret6, ssid7, ssid8, hide_ssid7, hide_ssid8, isolate7, isolate8, enc7, key7, enc8, key8, ssid7_vlan, ssid7_vlan_id, ssid8_vlan, ssid8_vlan_id, ssid7_ratelimit, ssid7_upload, ssid7_download, ssid8_ratelimit, ssid8_upload, ssid8_download, auth_server7, auth_port7, acct_secret7, slave_auth7, slave_auth_server7, slave_auth_port7, slave_acct_secret7, auth_server8, auth_port8, acct_secret8, slave_auth8, slave_auth_server8, slave_auth_port8, slave_acct_secret8, ssid9, ssid10, ssid11, ssid12, hide_ssid9, hide_ssid10, hide_ssid11, hide_ssid12, isolate9, isolate10, isolate11, isolate12, enc9, key9, enc10, key10, enc11, key11, enc12, key12, ssid9_vlan, ssid9_vlan_id, ssid10_vlan, ssid10_vlan_id, ssid11_vlan, ssid11_vlan_id, ssid12_vlan, ssid12_vlan_id, ssid9_ratelimit, ssid9_upload, ssid9_download, ssid10_ratelimit, ssid10_upload, ssid10_download, ssid11_ratelimit, ssid11_upload, ssid11_download, ssid12_ratelimit, ssid12_upload, ssid12_download, auth_server9, auth_port9, acct_secret9, slave_auth9, slave_auth_server9, slave_auth_port9, slave_acct_secret9, auth_server10, auth_port10, acct_secret10, slave_auth10, slave_auth_server10, slave_auth_port10, slave_acct_secret10, auth_server11, auth_port11, acct_secret11, slave_auth11, slave_auth_server11, slave_auth_port11, slave_acct_secret11, auth_server12, auth_port12, acct_secret12, slave_auth12, slave_auth_server12, slave_auth_port12, slave_acct_secret12, load_strategy_d5g, autohide_maxsta_d5g, autohide_resume_d5g, qos_atf_d5g, channel_d5g, min_signal_d5g, signal_str_d5g, studio_ssid_d5g, channel_width_d5g, advanced, beacon_interval, beacon_txpower, rts, hwmode, dis_legacy, mgmt_rate, advanced_5g, beacon_interval_5g, beacon_txpower_5g, rts_5g, hwmode_5g, advanced_d5g, beacon_interval_d5g, beacon_txpower_d5g, rts_d5g, hwmode_d5g
  id* (integer) — AP配置ID (主键)
  gid* (string) — AP所属分组ID，0表示未加入分组
  tagname* (string) — 标识名称（支持中文/数字/字母/下划线/连字符，不能以符号开头，1-15字符）
  comment* (string) — 备注信息，最多64个字符，不支持特殊字符
  mlo_radio0* (integer) — MLO radio0 2.4G频段开关
  mlo_radio1* (integer) — MLO radio1 5G R1频段开关
  mlo_radio2* (integer) — MLO radio2 5G R2频段开关
  flicker* (string) — 定位闪烁灯
  lights* (integer) — 状态灯开关
  ssid1* (string) — 2.4G SSID1
  ssid2* (string) — 2.4G SSID2
  hide_ssid1* (integer) — 隐藏2.4G SSID1开关
  hide_ssid2* (integer) — 隐藏2.4G SSID2开关
  isolate1* (integer) — 2.4G SSID1的访客模式开关
  isolate2* (integer) — 2.4G SSID2的访客模式开关
  qos_atf* (integer) — 2.4G的ATF公平调度算法
  load_strategy* (integer) — 2.4G负载策略
  autohide_maxsta* (integer) — 2.4G负载策略阀值1
  autohide_resume* (integer) — 2.4G负载策略阀值2
  max_pc* (integer) — 2.4G最大带机量
  channel* (integer) — 2.4G信道
  min_signal* (integer) — 2.4G最低连接信号
  enc1* (string) — 2.4G SSID1加密策略
  key1* (string) — 2.4G SSID1密码
  enc2* (string) — 2.4G SSID2加密策略
  key2* (string) — 2.4G SSID2密码
  ssid1_vlan* (string) — 2.4G SSID1 VLAN开关
  ssid1_vlan_id* (integer) — 2.4G SSID1 VLAN ID
  ssid2_vlan* (string) — 2.4G SSID2 VLAN开关
  ssid2_vlan_id* (integer) — 2.4G SSID2 VLAN ID
  ssid1_ratelimit* (integer) — 2.4G SSID1限速开关
  ssid1_upload* (integer) — 2.4G SSID1上行限速
  ssid1_download* (integer) — 2.4G SSID1下行限速
  ssid2_ratelimit* (integer) — 2.4G SSID2限速开关
  ssid2_upload* (integer) — 2.4G SSID2上行限速
  ssid2_download* (integer) — 2.4G SSID2下行限速
  auth_server1* (string) — 2.4G SSID1 RADIUS服务器IP
  auth_port1* (integer) — 2.4G SSID1 RADIUS服务端口
  acct_secret1* (string) — 2.4G SSID1 RADIUS密钥
  slave_auth1* (integer) — 2.4G SSID1备份RADIUS服务是否开启
  slave_auth_server1* (string) — 2.4G SSID1备份RADIUS服务器IP
  slave_auth_port1* (integer) — 2.4G SSID1备份RADIUS服务端口
  slave_acct_secret1* (string) — 2.4G SSID1备份RADIUS密钥
  auth_server2* (string) — 2.4G SSID2 RADIUS服务器IP
  auth_port2* (integer) — 2.4G SSID2 RADIUS服务端口
  acct_secret2* (string) — 2.4G SSID2 RADIUS密钥
  slave_auth2* (integer) — 2.4G SSID2备份RADIUS服务是否开启
  slave_auth_server2* (string) — 2.4G SSID2备份RADIUS服务器IP
  slave_auth_port2* (integer) — 2.4G SSID2备份RADIUS服务端口
  slave_acct_secret2* (string) — 2.4G SSID2备份RADIUS密钥
  signal_str* (integer) — 2.4G信号强度
  studio_ssid* (string) — 2.4G工作室SSID
  ssid3* (string) — 5G SSID1
  ssid4* (string) — 5G SSID2
  hide_ssid3* (integer) — 5G隐藏SSID1开关
  hide_ssid4* (integer) — 5G隐藏SSID2开关
  isolate3* (integer) — 5G SSID1访客模式开关
  isolate4* (integer) — 5G SSID2访客模式开关
  qos_atf_5g* (integer) — 5G ATF公平调度算法
  load_strategy_5g* (integer) — 5G负载策略
  autohide_maxsta_5g* (integer) — 5G负载策略阀值1
  autohide_resume_5g* (integer) — 5G负载策略阀值2
  max_pc_5g* (integer) — 5G最大带机量
  channel_5g* (integer) — 5G信道
  min_signal_5g* (integer) — 5G最低连接信号
  enc3* (string) — 5G SSID1加密策略
  key3* (string) — 5G SSID1密码
  enc4* (string) — 5G SSID2加密策略
  key4* (string) — 5G SSID2密码
  ssid3_vlan* (string) — 5G SSID1 VLAN开关
  ssid3_vlan_id* (integer) — 5G SSID1 VLAN ID
  ssid4_vlan* (string) — 5G SSID2 VLAN开关
  ssid4_vlan_id* (integer) — 5G SSID2 VLAN ID
  ssid3_ratelimit* (integer) — 5G SSID1限速开关
  ssid3_upload* (integer) — 5G SSID1上行限速
  ssid3_download* (integer) — 5G SSID1下行限速
  ssid4_ratelimit* (integer) — 5G SSID2限速开关
  ssid4_upload* (integer) — 5G SSID2上行限速
  ssid4_download* (integer) — 5G SSID2下行限速
  auth_server3* (string) — 5G SSID1 RADIUS服务器IP
  auth_port3* (integer) — 5G SSID1 RADIUS服务端口
  acct_secret3* (string) — 5G SSID1 RADIUS密钥
  slave_auth3* (integer) — 5G SSID1备份RADIUS服务是否开启
  slave_auth_server3* (string) — 5G SSID1备份RADIUS服务器IP
  slave_auth_port3* (integer) — 5G SSID1备份RADIUS服务端口
  slave_acct_secret3* (string) — 5G SSID1备份RADIUS密钥
  auth_server4* (string) — 5G SSID2 RADIUS服务器IP
  auth_port4* (integer) — 5G SSID2 RADIUS服务端口
  acct_secret4* (string) — 5G SSID2 RADIUS密钥
  slave_auth4* (integer) — 5G SSID2备份RADIUS服务是否开启
  slave_auth_server4* (string) — 5G SSID2备份RADIUS服务器IP
  slave_auth_port4* (integer) — 5G SSID2备份RADIUS服务端口
  slave_acct_secret4* (string) — 5G SSID2备份RADIUS密钥
  signal_str_5g* (integer) — 5G信号强度
  studio_ssid_5g* (string) — 5G工作室SSID
  task_switch1* (integer) — 开启时间计划任务1
  task_strategy1* (string) — 任务策略1
  task_date1* (string) — 任务日期1
  task_time1* (string) — 任务时间1
  task_switch2* (integer) — 开启时间计划任务2
  task_strategy2* (string) — 任务策略2
  task_date2* (string) — 任务日期2
  task_time2* (string) — 任务时间2
  task_switch3* (integer) — 开启时间计划任务3
  task_strategy3* (string) — 任务策略3
  task_date3* (string) — 任务日期3
  task_time3* (string) — 任务时间3
  reboot_strategy* (string) — 重启策略
  reboot_date* (string) — 重启日期
  channel_width_2g* (integer) — 2.4G频宽
  channel_width_5g* (integer) — 5G频宽
  port1_vlan* (string) — 端口1 VLAN开关
  port1_vlan_id* (integer) — 端口1 VLAN ID
  port2_vlan* (string) — 端口2 VLAN开关
  port2_vlan_id* (integer) — 端口2 VLAN ID
  port3_vlan* (string) — 端口3 VLAN开关
  port3_vlan_id* (integer) — 端口3 VLAN ID
  port4_vlan* (string) — 端口4 VLAN开关
  port4_vlan_id* (integer) — 端口4 VLAN ID
  ap_roaming* (integer) — AP快速漫游灵敏度设置
  perfer_5g* (integer) — 5G优先
  studio_mode* (integer) — 工作室模式开关
  gateway_check* (integer) — 网关检测开关
  country* (string) — 地区/国家码
  ssid_union* (integer) — 多频合一
  ssid5* (string) — 2.4G SSID3名称
  ssid6* (string) — 2.4G SSID4名称
  hide_ssid5* (integer) — 2.4G隐藏SSID3开关
  hide_ssid6* (integer) — 2.4G隐藏SSID4开关
  isolate5* (integer) — 2.4G SSID3访客模式开关
  isolate6* (integer) — 2.4G SSID4访客模式开关
  enc5* (string) — 2.4G SSID3加密策略
  key5* (string) — 2.4G SSID3密码
  enc6* (string) — 2.4G SSID4加密策略
  key6* (string) — 2.4G SSID4密码
  ssid5_vlan* (string) — 2.4G SSID3 VLAN开关
  ssid5_vlan_id* (integer) — 2.4G SSID3 VLAN ID
  ssid6_vlan* (string) — 2.4G SSID4 VLAN开关
  ssid6_vlan_id* (integer) — 2.4G SSID4 VLAN ID
  ssid5_ratelimit* (integer) — 2.4G SSID3限速开关
  ssid5_upload* (integer) — 2.4G SSID3上行限速
  ssid5_download* (integer) — 2.4G SSID3下行限速
  ssid6_ratelimit* (integer) — 2.4G SSID4限速开关
  ssid6_upload* (integer) — 2.4G SSID4上行限速
  ssid6_download* (integer) — 2.4G SSID4下行限速
  auth_server5* (string) — 2.4G SSID3 RADIUS服务器IP
  auth_port5* (integer) — 2.4G SSID3 RADIUS服务端口
  acct_secret5* (string) — 2.4G SSID3 RADIUS密钥
  slave_auth5* (integer) — 2.4G SSID3备份RADIUS服务是否开启
  slave_auth_server5* (string) — 2.4G SSID3备份RADIUS服务器IP
  slave_auth_port5* (integer) — 2.4G SSID3备份RADIUS服务端口
  slave_acct_secret5* (string) — 2.4G SSID3备份RADIUS密钥
  auth_server6* (string) — 2.4G SSID4 RADIUS服务器IP
  auth_port6* (integer) — 2.4G SSID4 RADIUS服务端口
  acct_secret6* (string) — 2.4G SSID4 RADIUS密钥
  slave_auth6* (integer) — 2.4G SSID4备份RADIUS服务是否开启
  slave_auth_server6* (string) — 2.4G SSID4备份RADIUS服务器IP
  slave_auth_port6* (integer) — 2.4G SSID4备份RADIUS服务端口
  slave_acct_secret6* (string) — 2.4G SSID4备份RADIUS密钥
  ssid7* (string) — 5G SSID3名称
  ssid8* (string) — 5G SSID4名称
  hide_ssid7* (integer) — 5G隐藏SSID3开关
  hide_ssid8* (integer) — 5G隐藏SSID4开关
  isolate7* (integer) — 5G SSID3访客模式开关
  isolate8* (integer) — 5G SSID4访客模式开关
  enc7* (string) — 5G SSID3加密策略
  key7* (string) — 5G SSID3密码
  enc8* (string) — 5G SSID4加密策略
  key8* (string) — 5G SSID4密码
  ssid7_vlan* (string) — 5G SSID3 VLAN开关
  ssid7_vlan_id* (integer) — 5G SSID3 VLAN ID
  ssid8_vlan* (string) — 5G SSID4 VLAN开关
  ssid8_vlan_id* (integer) — 5G SSID4 VLAN ID
  ssid7_ratelimit* (integer) — 5G SSID3限速开关
  ssid7_upload* (integer) — 5G SSID3上行限速
  ssid7_download* (integer) — 5G SSID3下行限速
  ssid8_ratelimit* (integer) — 5G SSID4限速开关
  ssid8_upload* (integer) — 5G SSID4上行限速
  ssid8_download* (integer) — 5G SSID4下行限速
  auth_server7* (string) — 5G SSID3 RADIUS服务器IP
  auth_port7* (integer) — 5G SSID3 RADIUS服务端口
  acct_secret7* (string) — 5G SSID3 RADIUS密钥
  slave_auth7* (integer) — 5G SSID3备份RADIUS服务是否开启
  slave_auth_server7* (string) — 5G SSID3备份RADIUS服务器IP
  slave_auth_port7* (integer) — 5G SSID3备份RADIUS服务端口
  slave_acct_secret7* (string) — 5G SSID3备份RADIUS密钥
  auth_server8* (string) — 5G SSID4 RADIUS服务器IP
  auth_port8* (integer) — 5G SSID4 RADIUS服务端口
  acct_secret8* (string) — 5G SSID4 RADIUS密钥
  slave_auth8* (integer) — 5G SSID4备份RADIUS服务是否开启
  slave_auth_server8* (string) — 5G SSID4备份RADIUS服务器IP
  slave_auth_port8* (integer) — 5G SSID4备份RADIUS服务端口
  slave_acct_secret8* (string) — 5G SSID4备份RADIUS密钥
  ssid9* (string) — 5G Radio2 SSID1名称
  ssid10* (string) — 5G Radio2 SSID2名称
  ssid11* (string) — 5G Radio2 SSID3名称
  ssid12* (string) — 5G Radio2 SSID4名称
  hide_ssid9* (integer) — 5G Radio2 SSID1隐藏开关
  hide_ssid10* (integer) — 5G Radio2 SSID2隐藏开关
  hide_ssid11* (integer) — 5G Radio2 SSID3隐藏开关
  hide_ssid12* (integer) — 5G Radio2 SSID4隐藏开关
  isolate9* (integer) — 5G Radio2 SSID1访客模式
  isolate10* (integer) — 5G Radio2 SSID2访客模式
  isolate11* (integer) — 5G Radio2 SSID3访客模式
  isolate12* (integer) — 5G Radio2 SSID4访客模式
  enc9* (string) — 5G Radio2 SSID1加密策略
  key9* (string) — 5G Radio2 SSID1密码
  enc10* (string) — 5G Radio2 SSID2加密策略
  key10* (string) — 5G Radio2 SSID2密码
  enc11* (string) — 5G Radio2 SSID3加密策略
  key11* (string) — 5G Radio2 SSID3密码
  enc12* (string) — 5G Radio2 SSID4加密策略
  key12* (string) — 5G Radio2 SSID4密码
  ssid9_vlan* (string) — 5G Radio2 SSID1 VLAN开关
  ssid9_vlan_id* (integer) — 5G Radio2 SSID1 VLAN ID
  ssid10_vlan* (string) — 5G Radio2 SSID2 VLAN开关
  ssid10_vlan_id* (integer) — 5G Radio2 SSID2 VLAN ID
  ssid11_vlan* (string) — 5G Radio2 SSID3 VLAN开关
  ssid11_vlan_id* (integer) — 5G Radio2 SSID3 VLAN ID
  ssid12_vlan* (string) — 5G Radio2 SSID4 VLAN开关
  ssid12_vlan_id* (integer) — 5G Radio2 SSID4 VLAN ID
  ssid9_ratelimit* (integer) — 5G Radio2 SSID1限速开关
  ssid9_upload* (integer) — 5G Radio2 SSID1上行限速
  ssid9_download* (integer) — 5G Radio2 SSID1下行限速
  ssid10_ratelimit* (integer) — 5G Radio2 SSID2限速开关
  ssid10_upload* (integer) — 5G Radio2 SSID2上行限速
  ssid10_download* (integer) — 5G Radio2 SSID2下行限速
  ssid11_ratelimit* (integer) — 5G Radio2 SSID3限速开关
  ssid11_upload* (integer) — 5G Radio2 SSID3上行限速
  ssid11_download* (integer) — 5G Radio2 SSID3下行限速
  ssid12_ratelimit* (integer) — 5G Radio2 SSID4限速开关
  ssid12_upload* (integer) — 5G Radio2 SSID4上行限速
  ssid12_download* (integer) — 5G Radio2 SSID4下行限速
  auth_server9* (string) — 5G Radio2 SSID1 RADIUS服务器IP
  auth_port9* (integer) — 5G Radio2 SSID1 RADIUS服务端口
  acct_secret9* (string) — 5G Radio2 SSID1 RADIUS密钥
  slave_auth9* (integer) — 5G Radio2 SSID1备份RADIUS服务是否开启
  slave_auth_server9* (string) — 5G Radio2 SSID1备份RADIUS服务器IP
  slave_auth_port9* (integer) — 5G Radio2 SSID1备份RADIUS服务端口
  slave_acct_secret9* (string) — 5G Radio2 SSID1备份RADIUS密钥
  auth_server10* (string) — 5G Radio2 SSID2 RADIUS服务器IP
  auth_port10* (integer) — 5G Radio2 SSID2 RADIUS服务端口
  acct_secret10* (string) — 5G Radio2 SSID2 RADIUS密钥
  slave_auth10* (integer) — 5G Radio2 SSID2备份RADIUS服务是否开启
  slave_auth_server10* (string) — 5G Radio2 SSID2备份RADIUS服务器IP
  slave_auth_port10* (integer) — 5G Radio2 SSID2备份RADIUS服务端口
  slave_acct_secret10* (string) — 5G Radio2 SSID2备份RADIUS密钥
  auth_server11* (string) — 5G Radio2 SSID3 RADIUS服务器IP
  auth_port11* (integer) — 5G Radio2 SSID3 RADIUS服务端口
  acct_secret11* (string) — 5G Radio2 SSID3 RADIUS密钥
  slave_auth11* (integer) — 5G Radio2 SSID3备份RADIUS服务是否开启
  slave_auth_server11* (string) — 5G Radio2 SSID3备份RADIUS服务器IP
  slave_auth_port11* (integer) — 5G Radio2 SSID3备份RADIUS服务端口
  slave_acct_secret11* (string) — 5G Radio2 SSID3备份RADIUS密钥
  auth_server12* (string) — 5G Radio2 SSID4 RADIUS服务器IP
  auth_port12* (integer) — 5G Radio2 SSID4 RADIUS服务端口
  acct_secret12* (string) — 5G Radio2 SSID4 RADIUS密钥
  slave_auth12* (integer) — 5G Radio2 SSID4备份RADIUS服务是否开启
  slave_auth_server12* (string) — 5G Radio2 SSID4备份RADIUS服务器IP
  slave_auth_port12* (integer) — 5G Radio2 SSID4备份RADIUS服务端口
  slave_acct_secret12* (string) — 5G Radio2 SSID4备份RADIUS密钥
  load_strategy_d5g* (integer) — 5G Radio2负载策略
  autohide_maxsta_d5g* (integer) — 5G Radio2负载策略阀值1
  autohide_resume_d5g* (integer) — 5G Radio2负载策略阀值2
  qos_atf_d5g* (integer) — 5G Radio2 ATF公平调度算法
  channel_d5g* (integer) — 5G Radio2信道
  min_signal_d5g* (integer) — 5G Radio2最低连接信号
  signal_str_d5g* (integer) — 5G Radio2信号强度
  studio_ssid_d5g* (string) — 5G Radio2工作室SSID列表
  channel_width_d5g* (integer) — 5G Radio2频宽
  advanced* (integer) — 2.4G高级设置开关
  beacon_interval* (integer) — 2.4G高级设置-beacon帧间隔
  beacon_txpower* (integer) — 2.4G高级设置-beacon发射功率
  rts* (integer) — 2.4G高级设置-RTS门限
  hwmode* (string) — 2.4G高级设置-射频工作模式
  dis_legacy* (string) — 2.4G高级设置-低速率接入限制
  mgmt_rate* (integer) — 2.4G高级设置-管理帧速率
  advanced_5g* (integer) — 5G Radio1高级设置开关
  beacon_interval_5g* (integer) — 5G Radio1高级设置-beacon帧间隔
  beacon_txpower_5g* (integer) — 5G Radio1高级设置-beacon发射功率
  rts_5g* (integer) — 5G Radio1高级设置-RTS门限
  hwmode_5g* (string) — 5G Radio1高级设置-射频工作模式
  advanced_d5g* (integer) — 5G Radio2高级设置开关
  beacon_interval_d5g* (integer) — 5G Radio2高级设置-beacon帧间隔
  beacon_txpower_d5g* (integer) — 5G Radio2高级设置-beacon发射功率
  rts_d5g* (integer) — 5G Radio2高级设置-RTS门限
  hwmode_d5g* (string) — 5G Radio2高级设置-射频工作模式

## APSSIDQuickUpdate
required: id, radio, ssid_index, ssid
  id* (integer) — AP配置ID
  radio* (string) — 射频选择；2g表示2.4G，5g表示5G
  ssid_index* (integer) — SSID序号，取值1-4
  ssid* (string) — Wi-Fi名称
  enc (string) — 加密方式
  key (string) — Wi-Fi密码；未传时保持当前密码，enc传off时清空密码
  hide (integer) — 隐藏Wi-Fi开关，1表示隐藏，0表示不隐藏
  isolate (integer) — 访客模式开关，1表示开启，0表示关闭
  vlan (string) — VLAN开关
  vlan_id (integer) — VLAN ID；vlan为on时取值1-4090
  channel (integer) — 所选射频的信道，0表示自动；radio为5g时非0值通常为36-165
  channel_width (integer) — 所选射频的频宽，2.4G支持0/20/40，5G支持20/40/80/160
  txpower (integer) — 所选射频的信号功率档位，取值0-5

## APSSIDUnionUpdate
required: id, ssid
  id* (integer) — AP配置ID
  ssid* (string) — 合并后的唯一Wi-Fi名称
  enc (string) — 合并后的加密方式
  key (string) — 合并后的Wi-Fi密码；未传时保持当前密码，enc传off时清空密码
  hide (integer) — 合并后的隐藏Wi-Fi开关，1表示隐藏，0表示不隐藏
  isolate (integer) — 合并后的访客模式开关，1表示开启，0表示关闭
  vlan (string) — 合并后的VLAN开关
  vlan_id (integer) — 合并后的VLAN ID；vlan为on时取值1-4090

## BackupSettingsRequest
required: id, enabled, strategy, time, cycle_time, valid_days
  id* (integer) — 当前备份策略记录ID
  enabled* (string) — 是否启用自动备份
  strategy* (string) — 备份周期类型：one=单次，week=每日/每周，month=每月
  time* (string) — 执行时间，格式 HH:mm
  cycle_time* (string) — 执行周期值，格式依 strategy 而定（见接口描述）
  valid_days* (integer) — 自动备份文件保留天数，0 表示不限期

## CpuFrequencyModeEditInput
required: mode, turbo
  mode* (string) — CPU调频模式
  turbo* (integer) — CPU睿频开关（0关闭，1开启）

## Dhcp6AccessModeInput
required: mode
  mode* (integer) — 访问控制模式，0:黑名单模式 1:白名单模式

## Dhcp6AccessRuleInput
required: enabled, mac, tagname
  enabled* (string) — 规则启用状态，yes为启用，no为停用
  mac* (string) — MAC地址
  tagname* (string) — 名称，支持中文、英文、数字、下划线和连字符，1-15个字符，不能以下划线或连字符开头
  comment (string) — 备注信息，最多64个字符，不支持特殊字符

## DhcpAccessModeInput
required: mode
  mode* (integer) — 访问控制模式，0:黑名单模式 1:白名单模式 2:同步安全中心MAC访问控制

## DnsConfigInput
required: enabled, forbid_dns_4a, cache_ttl, cachemode, proxy_force, proxy_force_dns, dns1, dns2, query, defense, network, query_args_ip, query_head_ip
  enabled* (string) — 启用DNS代理服务，yes为启用，no为停用
  forbid_dns_4a* (integer) — 忽略DNS 4A记录，0为允许，1为忽略
  cache_ttl* (integer) — 缓存的最大TTL（秒），范围 60-3600
  cachemode* (integer)
  proxy_force* (integer) — 强制客户端启用DNS代理（只针对dnsmasq），0为否，1为是
  proxy_force_dns* (string) — 第三方代理的DNS服务器IP列表，多个以逗号分隔，当 cachemode=2 时必填
  query* (string) — DoH解析URL地址，当 cachemode=3（DoH模式）时必填
  dns1* (string) — 主DNS服务器地址
  dns2* (string) — 备DNS服务器地址
  defense* (string) — DNS防御配置，详情回填后保存原值
  network* (string) — 网络接口配置，详情回填后保存原值
  query_args_ip* (string) — 查询参数IP，详情回填后保存原值
  query_head_ip* (string) — 查询头部IP，详情回填后保存原值

## FtpConfigEditInput
required: open_ftp, ftp_port, ftp_access
  open_ftp* (integer) — FTP服务开关（0关闭，1开启）
  ftp_port* (integer) — FTP服务端口，范围1-65535，但排除600-799、1234-1240、12345、34567
  ftp_access* (integer) — 是否允许外网访问（0不允许，1允许）

## Ikev2ServerConfigInput
required: id, enabled, authby, addrpool, secret, leftid, rightid, dns1, dns2, share_deny, mtu, privatekey, leftcert
  id* (integer) — 配置ID，必须传入
  enabled* (string) — 服务开启状态
  authby* (string) — 认证方式：secret-预共享密钥，mschapv2-EAP-MSCHAPv2
  addrpool* (string) — 客户端地址池，CIDR网络地址格式（如 10.6.1.0/24），必须为网络地址而非主机地址
  secret* (string) — 预共享密钥（authby=secret时必填，1-64个字符，）
  leftid* (string)
  rightid* (string) — 对端标识（1-100个字符，）
  dns1* (string) — DNS服务器1，必须为合法IP
  dns2* (string) — DNS服务器2，必须为合法IP
  share_deny* (integer) — 共享数超出处理动作
  mtu* (integer) — MTU值
  privatekey* (string) — 私钥，authby=mschapv2 时必填，使用转义后的单行 PEM 字符串传递：\n- 原始换行符替换为 `@`\n- 原始空格替换为 `#`\n按上述规则还原后，应得到可被 OpenSSL 正常识别的 PEM 私钥内容。\n
  leftcert* (string) — 本地证书，authby=mschapv2 时必填，使用转义后的单行 PEM 字符串传递：\n- 原始换行符替换为 `@`\n- 原始空格替换为 `#`\n按上述规则还原后，应得到可被 OpenSSL 以 X.509 证书方式正常解析的 PE

## KernelParamsEditInput
required: bbr, syn_recv_timeout, syn_send_timeout, established_timeout, fin_wait_timeout, last_ack_timeout, close_wait_timeout, time_wait_timeout, close_timeout, udp_timeout, udp_stream_timeout, icmp_timeout
  bbr* (integer) — BBR拥塞控制算法（0关闭，1开启）
  syn_recv_timeout* (integer) — SYN_RECV状态超时时间（秒）
  syn_send_timeout* (integer) — SYN_SEND状态超时时间（秒）
  established_timeout* (integer) — ESTABLISHED状态超时时间（秒）
  fin_wait_timeout* (integer) — FIN_WAIT状态超时时间（秒）
  last_ack_timeout* (integer) — LAST_ACK状态超时时间（秒）
  close_wait_timeout* (integer) — CLOSE_WAIT状态超时时间（秒）
  time_wait_timeout* (integer) — TIME_WAIT状态超时时间（秒）
  close_timeout* (integer) — CLOSE状态超时时间（秒）
  udp_timeout* (integer) — UDP数据包超时时间（秒）
  udp_stream_timeout* (integer) — UDP流超时时间（秒）
  icmp_timeout* (integer) — ICMP数据包超时时间（秒）

## L2tpServerConfigInput
required: enabled, server_ip, server_port, addr_pool, dns1, dns2, mtu, mru, force_ipsec
  enabled* (string) — 服务开启状态
  server_ip* (string) — 服务器地址，必须为合法IP
  server_port* (integer) — 服务器端口，不传时默认1701
  addr_pool* (string) — 客户端地址池
  dns1* (string) — DNS服务器1，必须为合法IP
  dns2* (string) — DNS服务器2，必须为合法IP
  mtu* (integer) — MTU值
  mru* (integer) — MRU值
  ipsec_secret (string) — IPSec预共享密钥
  leftid (string) — IPSec本地标识（允许为空，最多100个字符）
  rightid (string) — IPSec对端标识（允许为空，最多100个字符）
  force_ipsec* (integer) — 禁止非加密的连接，0为允许，1为禁止

## LanConfigUpdateRequest
required: bandif, bandmode, speed, duplex, lan_visit, ip_mask
  bandif* (string) — 绑定网卡MAC地址，多个以逗号分隔
  bandmode* (integer) — 绑定模式（0=网桥, 1=汇聚）
  speed* (integer) — 网卡速率（0=自动, 10/100/1000/10000 Mbps）
  duplex* (integer) — 工作模式（0=自动, 1=全双工, 2=半双工）
  lan_visit* (integer) — 是否允许其他LAN访问（0=不允许, 1=允许）
  ip_mask* (string) — IP地址和子网掩码，格式：IP/掩码，如 192.168.1.1/255.255.255.0
  mac (string) — 克隆MAC地址，空字符串表示不克隆
  comment (string) — 备注信息，最多64字符
  linkmode (integer) — 链路聚合模式，bandmode=1时有效（2=手工链路聚合, 4=LACP链路聚合）
  policy (integer) — 汇聚负载方式（0=layer2, 1=layer3+4, 2=layer2+3）

## LanLineCreateRequest
required: bandif
  bandif* (string) — 网卡MAC地址，不能与其他LAN或WAN接口已绑定的网卡重复

## MacAclModeInput
required: acl_mac
  acl_mac* (integer) — MAC访问控制模式

## OpenVpnServerConfigInput
required: enabled, proto, port, subnet, mask, tun_mtu, cipher, comp_lzo, dev_type, topology, method, ca, cert, key
  enabled* (string) — 服务开启状态
  proto* (string) — 协议类型
  port* (string) — 服务端口，1-65535
  subnet* (string) — VPN网段，必须为合法IP
  mask* (string) — 网段掩码，必须为合法IP
  tun_mtu* (string) — 隧道MTU，576-1500
  cipher* (string) — 加密算法（最多64个字符）
  comp_lzo* (string) — LZO压缩
  dev_type* (string) — 设备类型
  topology* (string) — 网络拓扑
  method* (integer) — 认证方法：0-账号认证，1-tls-auth，2-tls-crypt
  tls_auth (string) — TLS 认证密钥，method=1 或 method=2 时必填，使用转义后的单行 OpenVPN Static key 字符串传递：\n- 原始换行符替换为 `@`\n- 原始空格替换为 `#`\n按上述规则还原后，应得到合法的 Open
  ca* (string) — CA证书，使用转义后的单行 PEM 字符串传递：\n- 原始换行符替换为 `@`\n- 原始空格替换为 `#`\n按上述规则还原后，应得到可被 OpenSSL 以 X.509 证书方式正常解析的 PEM 内容。\n
  cert* (string) — 服务器证书，使用转义后的单行 PEM 字符串传递：\n- 原始换行符替换为 `@`\n- 原始空格替换为 `#`\n按上述规则还原后，应得到可被 OpenSSL 以 X.509 证书方式正常解析的 PEM 内容。\n
  key* (string) — 服务器私钥，使用转义后的单行 PEM 字符串传递：\n- 原始换行符替换为 `@`\n- 原始空格替换为 `#`\n按上述规则还原后，应得到可被 OpenSSL 正常识别的 PEM 私钥内容。\n
  push_gateway (string) — 推送网关
  push_route (string) — 推送路由
  push_route_comment (string) — 路由备注（最多64个字符）
  push_dns (string) — 推送DNS
  extra_config (string) — 额外配置

## PackageInput
required: packname, packtime, price, up_speed, down_speed
  packname* (string) — 套餐名称（必填，最多24个字符）
  packtime* (string)
  price* (integer) — 套餐价格
  up_speed* (integer) — 上行速率（KB/s）
  down_speed* (integer) — 下行速率（KB/s）
  comment (string) — 备注信息，最多64个字符，不支持特殊字符

## PppoeServerConfigInput
required: enabled, force_verify_name, server_ip, dns1, dns2, authmode, nas_identifier, nas_ip_address, radius_ip, secret, authport, accountport, addr_pool, interface, rate_limit_lan, drop_client, force_pppoe, enhance_check, share_deny, bind_vlan, verify_vlan, bind_iface, mtu, mru, lcp_echo_interval, lcp_echo_failure, maxconnect, restart_timer, comment
  enabled* (string) — 服务开启状态
  server_name (string) — 服务端名称
  force_verify_name* (integer) — 强制校验服务名称，0为不强制，1为强制，不传则不修改
  server_ip* (string) — 服务器地址，必须为合法IP
  dns1* (string) — DNS服务器1，必须为合法IP
  dns2* (string) — DNS服务器2，必须为合法IP
  authmode* (integer) — 认证方式：0-本地账户，1-本地账户空密码，2-任意用户，3-RADIUS
  nas_identifier* (string) — NAS标识（authmode=3时必填，1-60个字符）
  nas_ip_address* (string) — NAS IP地址（authmode=3时必填，合法IP）
  radius_ip* (string) — RADIUS服务端IP（authmode=3时必填）
  secret* (string) — 共享密钥（authmode=3时必填，1-60个字符）
  authport* (integer) — 认证端口（authmode=3时必填）
  accountport* (integer) — 记账端口（authmode=3时必填）
  addr_pool* (string) — 客户端地址池，格式为IP范围，多个用逗号分隔
  comment* (string) — 备注信息，最多64个字符，不支持特殊字符
  interface* (string) — 内网线路
  rate_limit_lan* (integer) — 对内网访问限速，0为关闭，1为开启
  drop_client* (integer) — 禁止客户端互访，0为关闭，1为开启
  force_pppoe* (integer) — 强制拨号上网，0为关闭，1为开启
  enhance_check* (integer) — 加强断线检测，0为关闭，1为开启
  share_deny* (integer) — 共享数超出处理动作：0-踢掉，1-拒绝连接
  bind_vlan* (integer) — 支持VLAN(QinQ)透传，0为关闭，1为开启
  verify_vlan* (integer) — 是否校验VLAN（仅bind_vlan=1时必填），0为不校验，1为校验
  bind_iface* (integer) — 支持绑定iface，0为关闭，1为开启
  mtu* (integer) — MTU值
  mru* (integer) — MRU值
  lcp_echo_interval* (integer) — LCP echo间隔（秒）
  lcp_echo_failure* (integer) — LCP echo失败次数
  maxconnect* (integer) — 客户端最大连接时长（小时），0表示不限制
  restart_timer* (integer) — 定时重启PPPoE服务，0为关闭，1为开启
  restart_week (string) — 定时重启周期，由星期数字组成（1=周一...7=周日），如1234567表示每天。仅restart_timer=1时必填
  restart_time (string) — 定时重启时间，格式HH:MM，多个用逗号分隔如06:00,18:00。仅restart_timer=1时必填

## PptpServerConfigInput
required: enabled, dns1, dns2, addr_pool, open_mppe, server_ip, server_port, mtu, mru
  enabled* (string) — 服务开启状态
  dns1* (string) — DNS服务器1，必须为合法IP
  dns2* (string) — DNS服务器2，必须为合法IP
  addr_pool* (string) — 客户端地址池
  open_mppe* (integer) — MPPE加密协议，0-关闭，1-强制开启，2-自动协商
  server_ip* (string) — 服务器地址，必须为合法IP
  server_port* (integer) — 服务器端口，不传时默认1723
  mtu* (integer) — MTU值
  mru* (integer) — MRU值

## RemoteAccessConfigInput
required: open_telnetd, open_wanweb, open_sshd, sshd_port, sshd_passwd, http_port, https_port, force_https
  open_telnetd* (integer) — 开启telnetd服务，0为关闭，1为开启
  open_wanweb* (integer) — 外网访问web管理权限，0为不允许访问，1为都允许，2为允许ipv4，3为允许ipv6
  open_sshd* (integer) — 开启SSHD服务，0为关闭，1为开启
  sshd_port* (integer) — SSHD服务端口，0表示关闭。允许范围10-599和800-65535，排除1234-1241、12345、34567
  sshd_passwd* (string) — SSHD登录密码
  http_port* (integer) — HTTP管理端口，0表示关闭HTTP。允许范围10-599和800-65535，排除1234-1241、12345、34567
  https_port* (integer) — HTTPS管理端口，0表示关闭HTTPS。允许范围10-599和800-65535，排除1234-1241、12345、34567
  force_https* (integer) — 强制使用HTTPS访问，访问HTTP时强制跳转HTTPS，0为不强制，1为强制

## SambaConfigEditInput
required: enabled, workgroup, wsdd2, access
  enabled* (string) — 开启或关闭状态
  workgroup* (string) — 工作组名称
  wsdd2* (integer) — 启用网络发现（0关闭，1开启）
  access* (integer) — 是否允许外网访问（0不允许，1允许）

## SecondaryRouteConfigInput
required: nol2rt, nol2rt_ip, ttl_num, time
  nol2rt* (integer) — 禁止二级路由开关（0:允许, 1:禁止）
  nol2rt_ip* ($ref:AddressObject)
  ttl_num* (integer) — 自定义TTL值
  time* ($ref:TimeObject)

## SecurityAdvancedConfigInput
required: noping_lan, noping_wan, notracert, hijack_ping, invalid, dos_lan, dos_lan_num, tcp_mss, tcp_mss_num
  noping_lan* (integer) — 禁止内网Ping（0:禁用, 1:启用）
  noping_wan* (integer) — 禁止外网Ping（0:禁用, 1:启用）
  notracert* (integer) — 禁止tracert追踪（0:禁用, 1:启用）
  hijack_ping* (integer) — 劫持Ping（0:禁用, 1:启用）
  invalid* (integer) — 禁止无效链接（0:禁用, 1:启用）
  dos_lan* (integer) — 内网DOS防御（0:禁用, 1:启用）
  dos_lan_num* (integer) — 内网DOS连接数限制
  tcp_mss* (integer) — 启用TCPMSS最大报文长度（0:禁用, 1:启用）
  tcp_mss_num* (integer) — TCPMSS最大报文长度

## SnmpdConfigEditInput
required: enabled, listen_port, syslocation, syscontact, sysname, version, community, source, rw, username, security, auth_proto, auth_pass, priv_proto, priv_pass
  enabled* (string) — 服务开启状态
  listen_port* (integer) — SNMP监听端口，范围 1-65535，600-799 为系统保留不可用
  syslocation* (string) — 物理位置信息
  syscontact* (string) — 联系信息
  sysname* (string) — 系统名称
  version* (integer) — SNMP版本（仅支持2和3）
  community* (string) — 团体名（v2使用），version=2时不可为空
  source* (string) — 可访问的IP地址/网段
  rw* (string) — 读写权限
  username* (string) — 用户名（v3使用），version=3时不可为空
  security* (string) — 安全级别（v3使用），version=3时必须为authNoPriv或authPriv
  auth_proto* (string) — 认证模式，security为authNoPriv或authPriv时必须为MD5或SHA
  auth_pass* (string) — 认证密码，security为authNoPriv或authPriv时必填，8-30字符
  priv_proto* (string) — 加密模式，security为authPriv时必须为DES或AES
  priv_pass* (string) — 加密密码，security为authPriv时必填，8-30字符

## SpeedTestStartRequest
  interface (string) — 测速线路名称，`all` 或空值表示由后端选择全部或默认外网线路；多个线路使用逗号分隔

## SystemBasicConfigInput
required: hostname, time_zone, time_zone_full, switch_nat, switch_ntp, switch_ntpd, switch_ntpserver, ntpserver_list, ntp_sync_cycle, link_mode, lan_nat, listenport, backport, language, fast_nat
  hostname* (string) — 主机名（1-21个字符，允许中文、字母、数字、`: @ - _ + .`）
  language* (integer) — 选择语言，1-中文，2-英文；企业版功能，免费版设置不生效
  time_zone* (integer) — 时区偏移量（UTC），如东八区为8
  time_zone_full* (string) — 国际时区全格式（例 0800），默认值 '0800'
  switch_nat* (integer) — 上网模式，0=NONAT，1=对称NAT，2=全锥形NAT
  switch_ntp* (integer) — 自动更新时间开关，0-关 1-开
  switch_ntpd* (integer) — ntpd 服务开关，0-关 1-开
  switch_ntpserver* (integer) — NTP 服务器开关，0-关 1-开
  ntpserver_list* (string) — 自定义 NTP 服务器列表，最长253个字符，支持 IPv4/IPv6/域名
  ntp_sync_cycle* (integer) — NTP 同步间隔（分钟）
  link_mode* (integer) — 链路模式，0=主干模式，1=旁路模式，2=SDWAN 桥
  lan_nat* (integer) — 路由模式(switch_nat=0)时是否启用 LAN 地址 NAT，0=关 1=开
  backport* (string) — 旁路模式上网接口
  listenport* (string) — 旁路模式监听接口
  fast_nat* (integer) — 加速模式，0关闭，1开启软件模式，企业版功能，免费版设置不生效

## TerminalInput
required: mac, tagname
  mac* (string) — MAC地址（唯一）
  tagname* (string) — 名称，支持中文、英文、数字、下划线和连字符，1-15个字符，不能以下划线或连字符开头
  comment (string) — 备注信息，最多64个字符，不支持特殊字符

## UserInput
required: username, passwd, enabled, ppptype, packages, upload, download, start_time, expires, share, ip_type, auto_mac, auto_vlanid, bind_vlanid, bind_ifname
  enabled* (string) — 账号状态
  comment (string) — 备注信息，最多64个字符，不支持特殊字符
  username* (string) — 用户名
  passwd* (string) — 密码（必填，最多64个字符）
  expires* (integer) — 过期日期（时间戳）
  start_time* (integer) — 开始日期（时间戳）
  ppptype* (string) — 拨号类型
  pppname (string) — PPPoE中继类型使用，选择外网接口
  share* (integer) — 共享数
  auto_mac* (integer) — 自动绑定MAC
  upload* (integer) — 上传限速（KB/s）
  download* (integer) — 下载限速（KB/s）
  ip_type* (integer) — IP类型（0:固定IP，1:地址池）
  src_addr (object) — 固定IP或地址池配置
  mac (string) — 绑定MAC地址
  address (string) — 住址
  name (string) — 姓名
  phone (string) — 手机号
  cardid (string) — 证件号码
  pppoev6_wan (string) — PPPoE接口继承WAN的前缀
  packages* (integer) — 套餐类型（对应套餐功能的id，id=0表示自定义）
  bind_vlanid* (string) — 绑定VLANID（0表示不绑定，支持格式2000/2000.400，数字范围1-4090）
  bind_ifname* (string) — 绑定网卡名称（any表示任意网卡）
  auto_vlanid* (integer) — 开启自动绑定VLAN

## UserUpdateInput
required: username, passwd, enabled, ppptype, packages, upload, download, start_time, expires, share, ip_type, auto_mac, auto_vlanid, bind_vlanid, pppname, pppoev6_wan, bind_ifname, src_addr, mac, address, name, phone, cardid, comment
  username* (string) — 用户名（编辑页不可修改，需带回原值）
  passwd* (string) — 密码（最多64个字符）
  enabled* (string) — 账号状态
  ppptype* (string) — 拨号类型
  packages* (integer) — 套餐类型（0表示自定义）
  upload* (integer) — 上传限速（KB/s）
  download* (integer) — 下载限速（KB/s）
  start_time* (integer) — 开始日期（时间戳）
  expires* (integer) — 过期日期（时间戳，0表示不过期）
  share* (integer) — 共享数
  ip_type* (integer) — IP类型（0:固定IP，1:地址池）
  auto_mac* (integer) — 自动绑定MAC
  auto_vlanid* (integer) — 开启自动绑定VLAN
  bind_vlanid* (string) — 绑定VLANID（0表示不绑定）
  pppname* (string) — PPPoE中继类型使用，选择外网接口
  pppoev6_wan* (string) — PPPoE接口继承WAN的前缀
  bind_ifname* (string) — 绑定网卡名称（any表示任意网卡）
  src_addr* (object) — 固定IP或地址池配置
  mac* (string) — 绑定MAC地址
  address* (string) — 住址
  name* (string) — 姓名
  phone* (string) — 手机号
  cardid* (string) — 证件号码
  comment* (string) — 备注信息，最多64个字符，不支持特殊字符

## VrrpConfigInput
required: enabled, type, prio, method, domain, dns, gateway, interval, ifnames, auto_sync, single_line, ignore_wanstatus, interfaces, virtual_ips, ht_iface, remote_addr
  enabled* (string) — 开启状态，yes为启用，no为停用
  type* (integer) — 工作模式，1=主备模式，3=负载模式
  prio* (integer) — 优先级
  method* (integer) — 探测方式，0=DNS+PING，1=DNS，2=PING
  domain* (string) — DNS探测域名
  dns* (string) — DNS服务地址
  gateway* (string) — PING 探测的目标 IP 地址
  interval* (integer) — 心跳间隔（秒）
  ifnames* (string) — 外网接口探测列表
  auto_sync* (integer) — 是否开启配置的自动同步（0=否，1=是），仅企业版支持
  single_line* (integer) — 是否开启单线环境（0=否，1=是）
  ignore_wanstatus* (integer) — 是否开启外网检测（0=否，1=是）
  interfaces* (string) — 传输链路接口列表
  virtual_ips* (string) — 传输链路对应接口的虚拟 IP，多个用逗号隔开
  ht_iface* (string) — 心跳接口
  remote_addr* (string) — 对端的 IP 地址（心跳线）

## WanConfigUpdateRequest
{description:"WAN接口配置更新请求体，按 `internet` 接入模式选择对应的参数结构：\n- `internet=0`（静态IP）：必填 `ip_mask`、`gateway` 及链路参数\n- `internet=1`（DHCP）：必填链路参数，可选 DHCP 扩展参数\n- `internet=2`（ADSL/PPPoE）：必填 `username`、`passwd` 及链路参数\n- `internet=3`（基于物理网卡混合模式）：子接口在 wan-vlan-config 中配置，可选多拨助手参数\n- `internet=4`（基于VLAN混合模式）：子接口在 wan-vlan-config 中配置\n",oneOf:[{$ref:"#/components/schemas/WanConfigStaticIPRequest"},{$ref:"#/compon

## WanLineCreateRequest
required: bandif
  bandif* (string) — 网卡MAC地址，不能与其他LAN或WAN接口已绑定的网卡重复

## WebAuthServiceConfigInput
required: enabled, max_time, idle_time, enc_ssid_noauth, timer_restart, timer_event, timer_restart_week, timer_restart_time, user_auth, coupon_auth, qq_auth, weibo_auth, phone_auth, redpacket_auth, static_pwd, nopasswd, weixin, weixin2, weixin_mini, facebook_auth, twitter_auth, google_auth, openapi_auth, custom_auth, hotel_auth, custom_appkey, authip_mode, allow_tryout, tryout_time, auto_auth, ldap_auth, popups, popups_ios, popups_android, auto_auth_timeout, api_switch, api_url, passwd, ipgroup, noauth_mac, whitelist, whitelist_https, whiteip, api_radius, imperceptible, macbind_server, nasname, radius_ip, radius_key, radius_authport, radius_accountport, radius_interval, radius_basip, api_ipchange_url, coupon_up, coupon_down, weixin_up, weixin_down, phone_up, phone_down, nopasswd_up, nopasswd_down, static_pwd_up, static_pwd_down, weibo_up, weibo_down, tryout_up, tryout_down, qq_up, qq_down, facebook_up, facebook_down, google_up, google_down, twitter_up, twitter_down, redpacket_up, redpacket_down, hotel_up, hotel_down, weixin_absorb, https_redirect, user_timeout, coupon_timeout, qq_timeout, weibo_timeout, phone_timeout, static_timeout, nopasswd_timeout, weixin_timeout, redpacket_timeout, facebook_timeout, google_timeout, twitter_timeout, tryout_timeout, hotel_timeout, user_max_time, user_idle_time, coupon_max_time, coupon_idle_time, qq_max_time, qq_idle_time, weibo_max_time, weibo_idle_time, phone_max_time, phone_idle_time, static_max_time, static_idle_time, nopasswd_max_time, nopasswd_idle_time, weixin_max_time, weixin_idle_time, facebook_max_time, facebook_idle_time, google_max_time, google_idle_time, twitter_max_time, twitter_idle_time, redpacket_max_time, redpacket_idle_time, tryout_max_time, tryout_idle_time, hotel_max_time, hotel_idle_time, uri_add_apinfo, sync_switch, interface, group_key, group_id, ldap_usergroup, ldap_url, ldap_port, ldap_mode, ldap_base, ldap_cname, ldap_admin_dn, ldap_admin_passwd, ldap_share_count, proxy_service, proxy_ipaddr
  enabled* (string) — 服务开启状态
  max_time* (integer) — 重新认证超时时间（分钟），0表示不限制
  idle_time* (integer) — 空闲时间自动下线（秒），0表示不限制
  enc_ssid_noauth* (integer) — 加密SSID免认证
  timer_restart* (integer) — 定时重新认证（定时全部踢下线）
  timer_event* (string) — 定时事件，默认为空；设置为period表示时间段开启认证
  timer_restart_week* (string) — 定时重新认证周期（1-7代表周一到周日）
  timer_restart_time* (string) — 定时重新认证时间，timer_event为period时为时间范围如08:00-18:00
  user_auth* (integer) — 用户密码认证
  coupon_auth* (integer) — 优惠券认证
  qq_auth* (integer) — QQ认证
  weibo_auth* (integer) — 微博认证
  phone_auth* (integer) — 手机认证
  redpacket_auth* (integer) — 红包认证
  static_pwd* (integer) — 固定密码认证
  nopasswd* (integer) — 一键认证（无密码）
  weixin* (integer) — 微信认证
  weixin2* (integer) — 微信扫码认证
  weixin_mini* (integer) — 微信小程序认证
  facebook_auth* (integer) — Facebook认证
  twitter_auth* (integer) — Twitter认证
  google_auth* (integer) — Google认证
  openapi_auth* (integer) — OpenAPI认证
  custom_auth* (integer) — 自定义认证
  hotel_auth* (integer) — 酒店认证
  custom_appkey* (string) — 自定义认证appkey
  authip_mode* (integer) — 认证IP方式（0全部IP认证，1部分IP认证）
  allow_tryout* (integer) — 允许试用
  tryout_time* (integer) — 试用时长（分钟）
  auto_auth* (integer) — 开启自动认证
  ldap_auth* (integer) — LDAP协议认证
  popups* (integer) — 开启portal弹窗
  popups_ios* (integer) — 开启iOS系统弹窗
  popups_android* (integer) — 开启安卓系统弹窗
  auto_auth_timeout* (integer) — 自动认证有效时长（天）
  api_switch* (integer) — 第三方对接开关
  api_url* (string) — 第三方对接跳转地址
  passwd* (string) — 固定密码（MD5哈希值）
  ipgroup* (string) — 认证IP群组，多个用逗号分隔，格式为IP范围如192.168.1.1-192.168.1.254
  noauth_mac* (string) — 免认证MAC地址，多个用逗号分隔
  whitelist* (string) — 白名单域名（HTTP），多个用逗号分隔
  whitelist_https* (string) — 白名单域名（HTTPS），多个用逗号分隔
  whiteip* (string) — 白名单IP，多个用逗号分隔
  api_radius* (integer) — 开启Radius对接
  imperceptible* (integer) — Radius无感知认证
  macbind_server* (string) — MAC绑定服务器地址，为空时使用radius_ip
  nasname* (string) — Radius NAS名称
  radius_ip* (string) — Radius服务器IP
  radius_key* (string) — Radius共享密钥
  radius_authport* (integer) — Radius认证端口
  radius_accountport* (integer) — Radius记账端口
  radius_interval* (integer) — 发送计费包间隔时长（秒）
  radius_basip* (string) — Portal回调Radius IP
  api_ipchange_url* (string) — 用户IP变更上报地址
  coupon_up* (integer) — 优惠券认证上传限速（KByte/s），0不限速
  coupon_down* (integer) — 优惠券认证下载限速（KByte/s），0不限速
  weixin_up* (integer) — 微信认证上传限速（KByte/s），0不限速
  weixin_down* (integer) — 微信认证下载限速（KByte/s），0不限速
  phone_up* (integer) — 手机认证上传限速（KByte/s），0不限速
  phone_down* (integer) — 手机认证下载限速（KByte/s），0不限速
  nopasswd_up* (integer) — 一键认证上传限速（KByte/s），0不限速
  nopasswd_down* (integer) — 一键认证下载限速（KByte/s），0不限速
  static_pwd_up* (integer) — 固定密码认证上传限速（KByte/s），0不限速
  static_pwd_down* (integer) — 固定密码认证下载限速（KByte/s），0不限速
  weibo_up* (integer) — 微博认证上传限速（KByte/s），0不限速
  weibo_down* (integer) — 微博认证下载限速（KByte/s），0不限速
  tryout_up* (integer) — 试用认证上传限速（KByte/s），0不限速
  tryout_down* (integer) — 试用认证下载限速（KByte/s），0不限速
  qq_up* (integer) — QQ认证上传限速（KByte/s），0不限速
  qq_down* (integer) — QQ认证下载限速（KByte/s），0不限速
  facebook_up* (integer) — Facebook认证上传限速（KByte/s），0不限速
  facebook_down* (integer) — Facebook认证下载限速（KByte/s），0不限速
  google_up* (integer) — Google认证上传限速（KByte/s），0不限速
  google_down* (integer) — Google认证下载限速（KByte/s），0不限速
  twitter_up* (integer) — Twitter认证上传限速（KByte/s），0不限速
  twitter_down* (integer) — Twitter认证下载限速（KByte/s），0不限速
  redpacket_up* (integer) — 红包认证上传限速（KByte/s），0不限速
  redpacket_down* (integer) — 红包认证下载限速（KByte/s），0不限速
  hotel_up* (integer) — 酒店认证上传限速（KByte/s），0不限速
  hotel_down* (integer) — 酒店认证下载限速（KByte/s），0不限速
  weixin_absorb* (integer) — 微信吸粉（开启后自动启用weixin2扫码）
  https_redirect* (integer) — HTTPS跳转portal页面
  user_timeout* (integer) — 用户密码认证独立超时开关
  coupon_timeout* (integer) — 优惠券认证独立超时开关
  qq_timeout* (integer) — QQ认证独立超时开关
  weibo_timeout* (integer) — 微博认证独立超时开关
  phone_timeout* (integer) — 手机认证独立超时开关
  static_timeout* (integer) — 固定密码认证独立超时开关
  nopasswd_timeout* (integer) — 一键认证独立超时开关
  weixin_timeout* (integer) — 微信认证独立超时开关
  redpacket_timeout* (integer) — 红包认证独立超时开关
  facebook_timeout* (integer) — Facebook认证独立超时开关
  google_timeout* (integer) — Google认证独立超时开关
  twitter_timeout* (integer) — Twitter认证独立超时开关
  tryout_timeout* (integer) — 试用认证独立超时开关
  hotel_timeout* (integer) — 酒店认证独立超时开关
  user_max_time* (integer) — 用户密码认证重新认证超时（分钟）
  user_idle_time* (integer) — 用户密码认证空闲超时下线（秒）
  coupon_max_time* (integer) — 优惠券认证重新认证超时（分钟）
  coupon_idle_time* (integer) — 优惠券认证空闲超时下线（秒）
  qq_max_time* (integer) — QQ认证重新认证超时（分钟）
  qq_idle_time* (integer) — QQ认证空闲超时下线（秒）
  weibo_max_time* (integer) — 微博认证重新认证超时（分钟）
  weibo_idle_time* (integer) — 微博认证空闲超时下线（秒）
  phone_max_time* (integer) — 手机认证重新认证超时（分钟）
  phone_idle_time* (integer) — 手机认证空闲超时下线（秒）
  static_max_time* (integer) — 固定密码认证重新认证超时（分钟）
  static_idle_time* (integer) — 固定密码认证空闲超时下线（秒）
  nopasswd_max_time* (integer) — 一键认证重新认证超时（分钟）
  nopasswd_idle_time* (integer) — 一键认证空闲超时下线（秒）
  weixin_max_time* (integer) — 微信认证重新认证超时（分钟）
  weixin_idle_time* (integer) — 微信认证空闲超时下线（秒）
  facebook_max_time* (integer) — Facebook认证重新认证超时（分钟）
  facebook_idle_time* (integer) — Facebook认证空闲超时下线（秒）
  google_max_time* (integer) — Google认证重新认证超时（分钟）
  google_idle_time* (integer) — Google认证空闲超时下线（秒）
  twitter_max_time* (integer) — Twitter认证重新认证超时（分钟）
  twitter_idle_time* (integer) — Twitter认证空闲超时下线（秒）
  redpacket_max_time* (integer) — 红包认证重新认证超时（分钟）
  redpacket_idle_time* (integer) — 红包认证空闲超时下线（秒）
  tryout_max_time* (integer) — 试用认证重新认证超时（分钟）
  tryout_idle_time* (integer) — 试用认证空闲超时下线（秒）
  hotel_max_time* (integer) — 酒店认证重新认证超时（分钟）
  hotel_idle_time* (integer) — 酒店认证空闲超时下线（秒）
  uri_add_apinfo* (integer) — portal页URL是否追加连接AP信息
  sync_switch* (integer) — 同步认证开关（开启后需配置interface、group_key、group_id）
  interface* (string) — 同步认证网卡接口
  group_key* (string) — 同步认证组密钥
  group_id* (integer) — 同步认证组播ID
  ldap_usergroup* (string) — LDAP用户所在组路径
  ldap_url* (string) — LDAP服务器地址
  ldap_port* (integer) — LDAP端口
  ldap_mode* (integer) — LDAP用户模式（0单用户组，1多用户组）
  ldap_base* (string) — LDAP base_dn
  ldap_cname* (string) — LDAP common name属性（cn或sAMAccountName）
  ldap_admin_dn* (string) — LDAP管理员全路径DN
  ldap_admin_passwd* (string) — LDAP管理员密码
  ldap_share_count* (integer) — LDAP允许同时上线个数（0表示不限制）
  proxy_service* (integer) — HTTPS 443代理服务
  proxy_ipaddr* (string) — HTTPS代理IP地址，未配置时为空

## WireguardTunnelInput
required: enabled, peer_publickey, allowips, comment, interface, keepalive
  enabled* (string) — 隧道启用状态，yes为启用，no为停用
  comment* (string) — 备注信息，最多64个字符，不支持特殊字符
  interface* (string) — WireGuard接口名称，以 wg 开头，例如 wg1
  peer_publickey* (string) — 对端公钥（Base64编码，44字符）
  presharedkey (string) — 预共享密钥（Base64编码，44字符，可选为空）
  allowips* (string) — 允许访问的IP地址范围
  endpoint (string) — 对端节点IP地址
  endpoint_port (integer) — 对端端口（可选，为空或合法端口号）
  keepalive* (integer) — 保活间隔（秒），范围 0-500，0 表示禁用
