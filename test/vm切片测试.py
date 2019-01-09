a = "Region=ITTE-CEE-E2E-R8C,CeeFunction=1,Tenant=689c319ac7a14aca86312c3e1036b275,VM=1693537ff-98f4-4e5b-b425-a5075189fd37"

#b = a.split("VM=")[-1]
c= a.split("Tenant=")
d = c[1].split(',')[0]

print c
print d
#print b,type(b)

compute_init="Pyhsical Storage Network Fault on compute-1209-2"
compute_original = compute_init.split('on ')[1]
print compute_original
