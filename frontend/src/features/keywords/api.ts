import { apiClient, apiDownload, apiRequest } from "@/lib/api/client";
import type { ImportResult, Keyword, KeywordFilters, KeywordList, KeywordStats, KeywordWrite } from "./types";
export function query(f:Omit<KeywordFilters,"page"|"pageSize">, paging=true, page=1, pageSize=20){const q=new URLSearchParams();if(paging){q.set("page",String(page));q.set("page_size",String(pageSize));}const map:Record<string,string>={platform:"platform",source:"source",city:"city",schoolStage:"school_stage",grade:"grade",subject:"subject",searchIntent:"search_intent",commercialIntent:"commercial_intent",contentStatus:"content_status",status:"status",search:"search"};Object.entries(map).forEach(([key,param])=>{if(f[key as keyof typeof f])q.set(param,String(f[key as keyof typeof f]));});return q.toString();}
export const listKeywords=(f:KeywordFilters)=>apiClient.get<KeywordList>(`/keywords?${query(f,true,f.page,f.pageSize)}`);
export const keywordStats=(f:KeywordFilters)=>apiClient.get<KeywordStats>(`/keywords/stats?${query(f,false)}`);
export const createKeyword=(v:KeywordWrite)=>apiClient.post<Keyword>("/keywords",v);
export const updateKeyword=(id:string,v:KeywordWrite)=>apiClient.put<Keyword>(`/keywords/${id}`,v);
export const deleteKeyword=(id:string)=>apiClient.delete<void>(`/keywords/${id}`);
export function importKeywords(file:File,confirm=false){const body=new FormData();body.append("file",file);return apiRequest<ImportResult>(`/keywords/import?confirm=${confirm}`,{method:"POST",body});}
export const exportKeywords=(f:KeywordFilters)=>apiDownload(`/keywords/export?${query(f,false)}`);
