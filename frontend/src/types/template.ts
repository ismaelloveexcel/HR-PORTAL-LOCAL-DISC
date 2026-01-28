export interface Template {
  id: number;
  name: string;
  type: string;
  content: string;
  version: number;
  created_by: string;
  created_at: string;
  is_active: boolean;
  revision_note?: string;
  parent_id?: number | null;
}

export interface TemplateCreate {
  name: string;
  type: string;
  content: string;
  revision_note?: string;
  parent_id?: number | null;
}
