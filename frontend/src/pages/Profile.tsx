import { useUser, useAuth } from '@clerk/clerk-react';
import { useEffect, useState } from 'react';

interface ProfileData {
  message: string;
  token: string;
}

export const Profile = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = await getToken();
        if (!token) return;

        const response = await fetch('http://localhost:8000/api/user/profile', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch profile');
        }
        
        const data: ProfileData = await response.json();
        setProfileData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    };

    if (user) {
      fetchProfile();
    }
  }, [user, getToken]);

  if (!user) return null;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <div className="mb-4">
        <p>Email: {user.primaryEmailAddress?.emailAddress}</p>
        <p>Name: {user.fullName}</p>
      </div>
      
      {error && (
        <div className="text-red-500 mb-4">
          Error: {error}
        </div>
      )}
      
      {profileData && (
        <div className="bg-gray-100 p-4 rounded">
          <pre>{JSON.stringify(profileData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
