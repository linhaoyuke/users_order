import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

export const formatDate = (date: string | Date, format = 'YYYY-MM-DD HH:mm:ss') => {
  return dayjs(date).format(format)
}

export const formatDateOnly = (date: string | Date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

export const formatTime = (date: string | Date) => {
  return dayjs(date).format('HH:mm:ss')
}

export const fromNow = (date: string | Date) => {
  return dayjs(date).fromNow()
}
