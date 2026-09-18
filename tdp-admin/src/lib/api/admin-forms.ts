import { requestAdminApi, type ReadAdminResourceOptions } from "./client";

export const adminFormsApi = {
  metadata: (
    workflow: string,
    objectId: string | number,
    options?: ReadAdminResourceOptions
  ) =>
    requestAdminApi(["admin-forms", workflow, String(objectId), "metadata"], {
      ...options,
      trailingSlash: true,
    }),
};
