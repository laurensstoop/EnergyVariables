# define the storage location
file_in1='/media/DataGate2/ERA5/BASE2'
file_out='/media/DataStager2/ERA5_BASE2_t2m'


months='01 02 03 04 05 06 07 08 09 10 11 12'
for Y in $(seq 1950 1978);do  
    for M in $months ; do
        cdo select,name=t2m ${file_in1}/ERA5-EU_${Y}${M}.nc ${file_out}/ERA5-EU_${Y}${M}.nc
    done
done

