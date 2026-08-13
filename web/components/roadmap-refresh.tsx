"use client";
import { useState } from "react";
import { JobMonitor } from "@/components/job-monitor";
export function RoadmapRefresh({ slug }: { slug: string }) { const [jobId,setJobId]=useState<string>(); async function run(){ const response=await fetch(`/api/roadmaps/${slug}/refresh`,{method:"POST"}); const body=await response.json(); if(response.ok)setJobId(body.jobId); } return <div className="stack"><button className="button green" onClick={run}>Generate update draft</button>{jobId&&<JobMonitor jobId={jobId}/>}</div>; }
