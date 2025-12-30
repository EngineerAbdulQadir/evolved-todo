"use client";

import { useState } from "react";
import { Building2, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createOrganization, type CreateOrganizationRequest } from "@/lib/api/organizations";

/**
 * CreateOrganizationDialog Component
 *
 * Dialog for creating a new organization with form validation.
 *
 * Task: T060 [P] [US1] - CreateOrganizationDialog component
 * References:
 * - frontend/lib/api/organizations.ts
 * - ADR-001: Multi-Tenant Data Isolation Strategy
 */

interface CreateOrganizationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateOrganizationDialog({
  isOpen,
  onClose,
  onSuccess,
}: CreateOrganizationDialogProps) {
  const [formData, setFormData] = useState<CreateOrganizationRequest>({
    name: "",
    slug: "",
    description: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleNameChange = (name: string) => {
    // Auto-generate slug from name
    const slug = name
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
      .replace(/^-+|-+$/g, "");

    setFormData({ ...formData, name, slug });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await createOrganization(formData);
      setFormData({ name: "", slug: "", description: "" });
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create organization");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({ name: "", slug: "", description: "" });
    setError(null);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px] rounded-none border-white/20 bg-black text-white font-mono">
        <DialogHeader className="border-b border-white/10 pb-4">
          <DialogTitle className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em]">
            <Building2 className="h-4 w-4" />
            Node_Creation_Protocol
          </DialogTitle>
          <DialogDescription className="text-[10px] uppercase tracking-widest text-neutral-500">
            Initialize new organization node in the neural network.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6 py-6">
            {/* Name Field */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">
                Organization_Identity <span className="text-white">*</span>
              </Label>
              <Input
                id="name"
                placeholder="ACME_SYSTEMS_GLOBAL"
                className="rounded-none border-neutral-800 bg-[#050505] text-xs font-mono focus:border-white focus:ring-0 placeholder:text-neutral-700"
                value={formData.name}
                onChange={(e) => handleNameChange(e.target.value)}
                required
                disabled={isLoading}
                autoFocus
              />
            </div>

            {/* Slug Field */}
            <div className="space-y-2">
              <Label htmlFor="slug" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">
                URL_Namespace <span className="text-white">*</span>
              </Label>
              <Input
                id="slug"
                placeholder="acme-systems-global"
                className="rounded-none border-neutral-800 bg-[#050505] text-xs font-mono focus:border-white focus:ring-0 placeholder:text-neutral-700"
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                required
                disabled={isLoading}
                pattern="[a-z0-9-]+"
                title="Only lowercase letters, numbers, and hyphens allowed"
              />
              <p className="text-[9px] text-neutral-600 uppercase tracking-tight">
                Namespace identifier. Lowercase_Alpha_Numeric only.
              </p>
            </div>

            {/* Description Field */}
            <div className="space-y-2">
              <Label htmlFor="description" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Description_MetaData</Label>
              <Textarea
                id="description"
                placeholder="Operational parameters and node objectives..."
                className="rounded-none border-neutral-800 bg-[#050505] text-xs font-mono focus:border-white focus:ring-0 placeholder:text-neutral-700 min-h-[100px]"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                disabled={isLoading}
                rows={3}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-950/20 border border-red-900/50 rounded-none">
                <p className="text-[10px] font-mono text-red-500 uppercase">{error}</p>
              </div>
            )}
          </div>

          <DialogFooter className="border-t border-white/10 pt-4 gap-4">
            <Button
              type="button"
              variant="outline"
              className="rounded-none border-neutral-800 text-neutral-500 hover:text-white hover:border-white hover:bg-white/5 text-[10px] font-bold uppercase tracking-widest"
              onClick={handleCancel}
              disabled={isLoading}
            >
              Abort_Session
            </Button>
            <Button 
                type="submit" 
                disabled={isLoading || !formData.name || !formData.slug}
                className="rounded-none bg-white text-black hover:bg-neutral-200 text-[10px] font-bold uppercase tracking-widest px-6"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Building2 className="mr-2 h-3 w-3" />
                  Initialize_Node
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
