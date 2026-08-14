export type Keyword = {
 id:string; organization_id:string; keyword:string; platform:string|null; source:string|null; city:string|null; school_stage:string|null; grade:string|null; subject:string|null; need_type:string|null; pain_point:string|null; search_intent:string|null; commercial_intent:"低"|"中"|"高"|null; content_status:"未使用"|"已进入选题"|"已发布"|"已复盘"|null; status:"启用"|"停用"|"待审核"; notes:string|null; created_at:string; updated_at:string; created_by:string|null; updated_by:string|null;
};
export type KeywordWrite = Omit<Keyword,"id"|"organization_id"|"created_at"|"updated_at"|"created_by"|"updated_by">;
export type KeywordList={items:Keyword[];total:number;page:number;page_size:number;total_pages:number};
export type KeywordStats={total:number;high_commercial_intent:number;unused:number;in_topics:number;platform_count:number;subject_count:number};
export type KeywordFilters={page:number;pageSize:number;platform:string;source:string;city:string;schoolStage:string;grade:string;subject:string;searchIntent:string;commercialIntent:string;contentStatus:string;status:string;search:string};
export type ImportResult={total_rows:number;success_count:number;failed_count:number;duplicate_count:number;errors:{row:number;field:string;message:string}[];preview:{row:number;keyword:string;platform:string|null;source:string|null}[];can_import:boolean};
export const emptyKeyword:KeywordWrite={keyword:"",platform:null,source:"人工录入",city:null,school_stage:null,grade:null,subject:null,need_type:null,pain_point:null,search_intent:null,commercial_intent:null,content_status:"未使用",status:"启用",notes:null};
