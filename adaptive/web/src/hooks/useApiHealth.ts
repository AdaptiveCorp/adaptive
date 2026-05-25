import { useQuery } from '@tanstack/react-query'
import client from '../api/client'

export function useApiHealth() {
  const { isSuccess } = useQuery({
    queryKey: ['api-health'],
    queryFn: () => client.get('/health'),
    refetchInterval: 30_000,
    retry: false,
  })

  return isSuccess
}
