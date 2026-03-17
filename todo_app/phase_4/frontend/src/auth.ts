// Mock auth for Phase 3 dev if actual auth not fully integrated
export const getSession = async () => {
    return {
        data: {
            user: { id: "rwnUVyxrNVk2tJX26AsYiMcqtSWnTKbb" },
            token: "mock-jwt-token"
        }
    }
}
