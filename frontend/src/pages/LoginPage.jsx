import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import AuthLayout from '../components/layout/AuthLayout';

export default function LoginPage() {
  const navigate = useNavigate();
  const { error, success } = useToast();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await login(email, password);
      success('Login successful');
      navigate('/');
    } catch (err) {
      error(err?.message || 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      heroTitle="Where your drafts live"
      heroDescription="Your posts, their sources, your share links and reader numbers — all kept together under your account."
      featurePoints={[
        'Every post stays private to your account until you choose to share it.',
        'Public share links report real reader feedback back to you.',
      ]}
      formTitle="Sign in"
      formDescription="Use the email and password tied to your account."
      footer={(
        <>
          New here?{' '}
          <Link to="/register" className="link-editorial">
            Create an account
          </Link>
        </>
      )}
    >
      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <div>
          <label htmlFor="login-email" className="field-label">
            Email address
          </label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="you@example.com"
            className="input-editorial"
          />
        </div>

        <div>
          <label htmlFor="login-password" className="field-label">
            Password
          </label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            placeholder="Enter your password"
            className="input-editorial"
          />
        </div>

        <Button
          type="submit"
          variant="ink"
          isLoading={isSubmitting}
          className="w-full justify-center py-3"
        >
          Sign in
        </Button>
      </form>
    </AuthLayout>
  );
}
