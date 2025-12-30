export interface Team {
  id: string;
  name: string;
  description?: string;
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}