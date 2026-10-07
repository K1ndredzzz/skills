# 任务包与结果

主代理在用户私有工作目录单独维护dispatch.json：run_id、pilot_gate、资料/简历版本、获准岗位列表、账号域别名、锁所有者/状态。账号别名不含手机号。每代理独占任务目录并写自己的result.json；不并发追加总台账。

## 子代理任务包

```text
任务ID与阶段：<核验准备 / 试填保存 / 正式申请>
目标：<雇主、机构、岗位名、代码、官方入口、志愿顺序>
已有申请：<草稿/已投/结果未知，以及证据>
资料：<总表路径及版本；指定简历路径及哈希；必要证明路径>
授权：<用户原意、适用范围、提交权限、已回答声明与调剂>
账号域/写锁：<匿名域、持有或只读等待、锁所有者>
独占会话/标签：<由主代理分配的id>
输出：<独占目录>
禁止修改：总表、简历源文件、其他任务文件及会话。
职责：核验岗位/已有记录，读取实际要求，填写并复核；获准且齐全时提交并核验结果。
缺项/冲突：记录字段原文、证据与受影响步骤，交主代理集中处理；继续独立工作。
停止条件：需本人登录/上传、工具拒绝、未决提交；保存检查点，不绕过或重提。
交付：result.json加简短回报；有明确已提交证据才能用submitted_verified。
```

## 单任务结果示例

```json
{
  "task_id": "a",
  "status": "manual_step_required",
  "employer": "employer-a",
  "job_id": "observed-job-id",
  "state_domain": "shared-account-1",
  "session": "exclusive-session",
  "profile_version": "version",
  "resume_version": "hash",
  "saved_modules": ["education", "language"],
  "blocking_fields": [],
  "side_effects": ["first-preference-confirmed"],
  "manual_step": "Upload the specified local life photo; file chooser failed",
  "submission": {"attempted": false, "application_id": null, "submitted_at": null, "evidence": []},
  "next_action": "Verify attachments and preview before submitting",
  "lock_handoff": "coordinator must check no pending write"
}
```

状态：prepared、filling、draft_saved、needs_information、manual_step_required、submission_unknown、submitted_verified、ineligible、failed。

等待试投成功或账号写锁的任务使用prepared，并在next_action及调度清单注明wait_for_pilot或wait_for_lock，不能算作已开始填写。

submitted_verified必须有平台明确已提交状态的证据；不提供编号的平台用岗位+已提交状态+时间，不造编号。submission_unknown核验前保留账号锁；提交超时不是重提理由。崩溃恢复须确认旧代理不再写、没有悬而未决的提交和旧表单覆盖风险。

主代理逐岗位汇总真实状态、保存进度、证据和阻塞。仅将需用户的信息/操作集中提出。某账号域停住时，其他独立域继续。
