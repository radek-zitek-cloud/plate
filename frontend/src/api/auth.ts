import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type LoginRequest = {
  username: string;
  password: string;
}

export type SignupRequest = {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export type User = {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

export type LoginResponse = {
  access_token: string;
  token_type: string;
}

export type UpdateProfileRequest = {
  email?: string;
  username?: string;
  full_name?: string;
}

export type PasswordChangeRequest = {
  current_password: string;
  new_password: string;
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await api.post<LoginResponse>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  signup: async (data: SignupRequest): Promise<User> => {
    const response = await api.post<User>('/api/v1/users/signup', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/api/v1/users/me');
    return response.data;
  },

  testToken: async (): Promise<User> => {
    const response = await api.post<User>('/api/v1/auth/test-token');
    return response.data;
  },
};

export const updateProfile = async (data: UpdateProfileRequest): Promise<User> => {
  const response = await api.put<User>('/api/v1/users/me', data);
  return response.data;
};

export const changePassword = async (data: PasswordChangeRequest): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>('/api/v1/users/me/password', data);
  return response.data;
};

export default api;
