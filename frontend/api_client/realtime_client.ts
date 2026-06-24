import { RealtimeChannel } from '@supabase/supabase-js'
import { getSupabaseBrowserClient } from './auth_client'

export class RealtimeClient {
  private channels: Map<string, RealtimeChannel> = new Map();

  subscribeToTable(
    tableName: string, 
    callback: (payload: any) => void,
    schema: string = 'public'
  ): RealtimeChannel {
    const supabase = getSupabaseBrowserClient()
    const channelName = `${schema}:${tableName}`

    if (this.channels.has(channelName)) {
      return this.channels.get(channelName)!
    }

    const channel = supabase
      .channel(`db-changes-${tableName}`)
      .on(
        'postgres_changes',
        { event: '*', schema, table: tableName },
        callback
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscribed to realtime events on ${tableName}`)
        }
      })

    this.channels.set(channelName, channel)
    return channel
  }

  unsubscribe(tableName: string, schema: string = 'public') {
    const channelName = `${schema}:${tableName}`
    const channel = this.channels.get(channelName)
    if (channel) {
      const supabase = getSupabaseBrowserClient()
      supabase.removeChannel(channel)
      this.channels.delete(channelName)
    }
  }

  unsubscribeAll() {
    const supabase = getSupabaseBrowserClient()
    supabase.removeAllChannels()
    this.channels.clear()
  }
}

export const realtimeClient = new RealtimeClient();
