from cnm.data.file_era_times import FileEraTimes
from cnm.config import WEB_DATA


def get_era_times(scheduler, network_config):
    print(f"Starting: Calc era times for {network_config.name}.")
    fet = FileEraTimes(network_config, WEB_DATA)
    fet.from_rpc_query()
    fet.save()
    scheduler.add_job(id=f"era_times_{network_config.name}",
                      func=get_era_times,
                      trigger='date',
                      run_date=fet.next_query_time,
                      args=[scheduler, network_config])
    print(f"Finished: Calc era times for {network_config.name}. Next run {fet.next_query_time}")
