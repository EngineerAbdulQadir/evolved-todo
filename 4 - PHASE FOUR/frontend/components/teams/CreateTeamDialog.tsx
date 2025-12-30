"use client";

import { useState } from "react";
import { Users, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createTeam, type CreateTeamRequest } from "@/lib/api/teams";

/**
 * CreateTeamDialog Component
 *
 * Dialog for creating a new team within an organization.
 *
 * Task: T091 [P] [US2] - CreateTeamDialog component
 * References:
 * - frontend/lib/api/teams.ts
 * - ADR-001: Multi-Tenant Data Isolation Strategy
 * - ADR-002: RBAC Middleware Architecture
 */

interface CreateTeamDialogProps {
  isOpen: boolean;
  organizationId: string;
  organizationName?: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateTeamDialog({
  isOpen,
  organizationId,
  organizationName,
  onClose,
  onSuccess,
}: CreateTeamDialogProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const requestData: CreateTeamRequest = {
        name: formData.name,
        description: formData.description || undefined,
        organization_id: organizationId,
      };

      await createTeam(requestData);
      setFormData({ name: "", description: "" });
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create team");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({ name: "", description: "" });
    setError(null);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Create Team
          </DialogTitle>
          <DialogDescription>
            {organizationName ? (
              <>Create a new team in <strong>{organizationName}</strong></>
            ) : (
              <>Create a new team to organize your work</>
            )}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {/* Name Field */}
            <div className="space-y-2">
              <Label htmlFor="name">
                Team Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                placeholder="Engineering"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                disabled={isLoading}
                autoFocus
              />
              <p className="text-xs text-gray-500">
                Examples: Engineering, Marketing, Design, Sales
              </p>
            </div>

            {/* Description Field */}
            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                placeholder="A brief description of the team's purpose and goals..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                disabled={isLoading}
                rows={3}
              />
            </div>

            {/* Info Box */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-xs text-blue-600">
                <strong>Note:</strong> You need organization admin or owner permissions to create teams.
                Team members can be added after creation.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || !formData.name.trim()}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Users className="mr-2 h-4 w-4" />
                  Create Team
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
