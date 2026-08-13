import { db } from "@/lib/db";
import { formatCost, formatDate } from "@/lib/format";

export default async function RunsPage() {
  const jobs = await db()`
    select j.*, coalesce((select sum(total_cost_usd) from agent_runs ar where ar.job_id=j.id),0) as cost
    from jobs j order by created_at desc limit 150`;
  return <div className="page"><header className="page-head"><div><div className="eyebrow">Background work</div><h1>Runs</h1><p className="lead">每个长任务都有 durable state、阶段、重试、费用和可恢复的部分结果。</p></div></header><div className="card">{jobs.length ? jobs.map((job)=><div className="item-row" key={job.id}><div className="row"><div><div className="item-title">{job.job_type}</div><div className="meta"><span>{formatDate(job.created_at)}</span><span>{job.current_stage??"queued"}</span><span>attempt {job.attempts}/{job.max_attempts}</span><span>{formatCost(job.cost)}</span></div></div><span className={`badge ${job.status==="succeeded"?"green":job.status==="dead"?"red":"amber"}`}>{job.status}</span></div><div className="progress" style={{marginTop:10}}><span style={{width:`${Number(job.progress)}%`}}/></div></div>):<div className="empty">No background runs.</div>}</div></div>;
}
